import streamlit as st
import time
from experiment import Experiment
from ui import display_boxes, show_instructions, show_feedback
from data import save_round_data, save_questionnaire, get_unique_filename
from questionnaires import post_phase_questionnaire, debrief_questionnaire
from constants import PHASES, ROUNDS_PER_PHASE

# Session state initialization
def init_session():
    st.session_state['step'] = 'welcome'
    st.session_state['participant_id'] = ''
    st.session_state['professional_area'] = ''
    st.session_state['phase_idx'] = 0
    st.session_state['experiment'] = None
    st.session_state['round'] = 1
    st.session_state['last_result'] = None
    st.session_state['last_reward'] = None
    st.session_state['last_box'] = None
    st.session_state['show_feedback'] = False
    st.session_state['start_time'] = None
    st.session_state['questionnaire'] = {}
    st.session_state['all_questionnaire_data'] = []  # Store all phase questionnaires
    st.session_state['phase_order'] = None
    st.session_state['phase_complete'] = False
    st.session_state['all_done'] = False
    st.session_state['awaiting_choice'] = True
    st.session_state['last_special'] = None
    st.session_state['exited'] = False
    st.session_state['exit_time'] = None
    st.session_state['box_chosen'] = None
    st.session_state['last_round_message'] = ""
    st.session_state['last_message_type'] = 'info'
    st.session_state['earnings_history'] = []
    st.session_state['round_history'] = []
    st.session_state['start_clicked'] = False
    st.session_state['begin_rounds_clicked'] = False
    st.session_state['submit_questionnaire_clicked'] = False
    st.session_state['submit_debrief_clicked'] = False
    st.session_state['restart_clicked'] = False
    st.session_state['final_submission_complete'] = False
    # Unique session id for deduplication and tracing
    st.session_state['session_id'] = str(int(time.time()))

if 'step' not in st.session_state:
    init_session()

# --- Callback functions ---
def start_experiment():
    st.session_state['step'] = 'enter_id'
    st.session_state['start_clicked'] = False

def set_participant_id():
    participant_id = st.session_state.get('participant_id_input', '')
    professional_area = st.session_state.get('professional_area_input', '')
    
    # Validate inputs
    if not participant_id.isdigit():
        st.warning("Please enter a valid numeric participant ID.")
        return
    
    if professional_area == "Select your professional area" or not professional_area:
        st.warning("Please select your professional area.")
        return
    
    # Store validated inputs
    st.session_state['participant_id'] = int(participant_id)
    st.session_state['professional_area'] = professional_area
    
    # Initialize experiment
    exp = Experiment(st.session_state['participant_id'])
    st.session_state['phase_order'] = exp.phase_order
    st.session_state['experiment'] = exp
    st.session_state['step'] = 'instructions'


def begin_rounds():
    st.session_state['step'] = 'rounds'
    st.session_state['start_time'] = time.time()
    st.session_state['phase_complete'] = False
    actual_phase = st.session_state['phase_order'][st.session_state['phase_idx']]
    st.session_state['experiment'].reset_for_phase(actual_phase)
    st.session_state['awaiting_choice'] = True
    st.session_state['last_result'] = None
    st.session_state['last_reward'] = None
    st.session_state['last_box'] = None
    st.session_state['last_special'] = None
    # Clear the message when starting a new phase
    st.session_state['last_round_message'] = ""
    st.session_state['last_message_type'] = 'info'
    # Reset earnings history for new phase
    st.session_state['earnings_history'] = []
    st.session_state['round_history'] = []
    st.session_state['begin_rounds_clicked'] = False

def choose_box_a():
    st.session_state['box_chosen'] = 'A'

def choose_box_b():
    st.session_state['box_chosen'] = 'B'

# Removed next_round function as auto-advance is implemented

def submit_questionnaire():
    exp = st.session_state['experiment']
    actual_phase = exp.phase
    responses = st.session_state.get('current_questionnaire_responses', {})
    # Only store questionnaire responses for batch sending later
    questionnaire_entry = {
        'session_id': st.session_state['session_id'],
        'participant_id': st.session_state['participant_id'],
        'professional_area': st.session_state['professional_area'],
        'phase': actual_phase,
        **responses
    }
    st.session_state['all_questionnaire_data'].append(questionnaire_entry)
    st.session_state['phase_complete'] = False
    if st.session_state['phase_idx'] < 2:
        st.session_state['phase_idx'] += 1
        st.session_state['step'] = 'instructions'
    else:
        st.session_state['all_done'] = True
        st.session_state['step'] = 'debrief'


def submit_debrief_callback():
    # Immediately mark complete to disable further clicks
    st.session_state['final_submission_complete'] = True
    # Retrieve stored responses
    feedback = st.session_state.get('current_debrief_responses', {})
    debrief_entry = {
        'session_id': st.session_state['session_id'],
        'participant_id': st.session_state['participant_id'],
        'professional_area': st.session_state['professional_area'],
        'phase': 'debrief',
        **feedback
    }
    st.session_state['all_questionnaire_data'].append(debrief_entry)

    from data import save_questionnaire, save_round_data

    # Save questionnaires
    save_questionnaire(
        st.session_state['participant_id'], 'batch', st.session_state['all_questionnaire_data']
    )
    # Save experiment data
    exp = st.session_state.get('experiment')
    if exp and exp.data:
        save_round_data(
            exp.data,
            st.session_state['participant_id'],
            initial_probs=exp.get_initial_probs(),
            seeds=exp.get_seeds()
        )
    st.session_state['step'] = 'thank_you'

def restart_experiment():
    st.session_state['restart_clicked'] = True

# --- Screens ---
def welcome_screen():
    st.title("Welcome to the Decision Experiment")
    st.markdown("""
    Thank you for participating in this experiment!

    This experiment is conducted as part of a bachelor’s project in the International Finance program at Frankfurt University of Applied Sciences.

    During the experiment, you will repeatedly choose between two decision options—presented as boxes. Each box offers different potential payouts, some of which are associated with probabilities. To assist you, visualizations will be shown that illustrate the respective winning probabilities and possible payouts.

    Please make your decisions carefully and spontaneously. There are no right or wrong answers—what matters is your personal assessment.

    🕒 Total duration: approx. 10–15 minutes.
    """)
    st.button('Start', on_click=start_experiment)

def id_screen():
    st.subheader("Enter your participant ID")
    st.text_input("Participant ID (numbers only)", key='participant_id_input', max_chars=5)
    
    st.subheader("Professional Area")
    professional_areas = [
        "Select your professional area",
        "Student", 
        "Financial/Banking", 
        "Social Sciences", 
        "Information Technology", 
        "Engineering", 
        "Healthcare/Medicine", 
        "Education", 
        "Business/Management", 
        "Law/Legal", 
        "Arts/Creative", 
        "Science/Research", 
        "Other"
    ]
    st.selectbox(
        "What is your professional area?", 
        professional_areas, 
        key='professional_area_input'
    )
    
    st.button('Start Experiment', on_click=set_participant_id)

def instructions_screen():
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = st.session_state['phase_order'][st.session_state['phase_idx']]
    st.subheader(f"Phase {display_phase_num} - Instructions")
    show_instructions(actual_phase)
    st.button('Begin Rounds', on_click=begin_rounds)

def rounds_screen():
    exp = st.session_state['experiment']
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = exp.phase
    st.markdown(f"**Phase {display_phase_num} Instructions:**")
    show_instructions(actual_phase)
    st.subheader(f"Phase {display_phase_num} - Round {exp.round} of {ROUNDS_PER_PHASE}")
    st.write(f"Cumulative earnings: {exp.cumulative_earnings} € 💵")
    
    # Display persistent result message from last round with appropriate color
    if st.session_state.get('last_round_message'):
        message_type = st.session_state.get('last_message_type', 'info')
        if message_type == 'success':
            st.success(st.session_state['last_round_message'])
        elif message_type == 'error':
            st.error(st.session_state['last_round_message'])
        elif message_type == 'warning':
            st.warning(st.session_state['last_round_message'])
        else:
            st.info(st.session_state['last_round_message'])
    
    st.write("Choose a box:")
    
    display_boxes(actual_phase, exp.p_safe, exp.p_uncertain)
    
    # Add spacing between boxes and buttons
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button('Box A', key=f"A_{display_phase_num}_{exp.round}", on_click=choose_box_a)
    with col2:
        st.button('Box B', key=f"B_{display_phase_num}_{exp.round}", on_click=choose_box_b)
    
    # Display earnings timeline graph at the bottom - only when not transitioning to questionnaire
    if st.session_state['earnings_history'] and not st.session_state.get('phase_complete', False):
        st.subheader("Cumulative Earnings Timeline")
        import plotly.express as px
        import pandas as pd
        
        # Create a DataFrame for the timeline
        timeline_df = pd.DataFrame({
            'Round': st.session_state['round_history'],
            'Cumulative Earnings (€)': st.session_state['earnings_history']
        })
        
        # Create the line chart
        fig = px.line(timeline_df, 
                     x='Round', 
                     y='Cumulative Earnings (€)',
                     title=f"Phase {display_phase_num} - Earnings Progress",
                     markers=True)
        
        # Customize the chart
        fig.update_layout(
            height=400,  # Increased height
            showlegend=False,
            xaxis_title="Round",
            yaxis_title="Cumulative Earnings (€)"
        )
        
        # Add horizontal line at y=0
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
        
        # Remove toolbar icons and display options
        config = {
            'displayModeBar': False,  # This removes all the toolbar icons
            'staticPlot': False  # Keep it interactive for hover, but no toolbar
        }
        
        st.plotly_chart(fig, use_container_width=True, config=config)
    
    # Handle box choice
    if st.session_state.get('box_chosen'):
        box_chosen = st.session_state['box_chosen']
        decision_time = time.time() - st.session_state['start_time']
        result, reward, special = exp.draw_ball(box_chosen)
        exp.cumulative_earnings += reward
        exp.data.append([
            st.session_state['session_id'],
            st.session_state['participant_id'], st.session_state['professional_area'], 
            actual_phase, exp.round, box_chosen, round(decision_time, 3), result, reward, 
            exp.cumulative_earnings, round(exp.p_safe, 3), round(exp.p_uncertain, 3)
        ])
        exp.adjust_probabilities(box_chosen)
        
        # Update the persistent message for this round with appropriate color
        if result == 'red':
            st.session_state['last_round_message'] = f"You drew a red ball from Box {box_chosen} (+{reward} €)"
            st.session_state['last_message_type'] = 'success'  # Green for positive
        elif result == 'black':
            st.session_state['last_round_message'] = f"You drew a black ball from Box {box_chosen} ({reward} €)"
            st.session_state['last_message_type'] = 'error'  # Red for negative
        elif result == 'gold':
            st.session_state['last_round_message'] = f"🏆 Surprise! You drew a gold ball from Box {box_chosen} (+{reward} €)"
            st.session_state['last_message_type'] = 'warning'  # Gold/yellow for positive surprise
        elif result == 'silver':
            st.session_state['last_round_message'] = f"💿 Oh no! You drew a silver ball from Box {box_chosen} ({reward} €)"
            st.session_state['last_message_type'] = 'error'  # Red for negative surprise
        
        # Update earnings history for the timeline graph
        st.session_state['earnings_history'].append(exp.cumulative_earnings)
        st.session_state['round_history'].append(exp.round)
        
        st.session_state['start_time'] = time.time()
        st.session_state['box_chosen'] = None
        
        # Auto-advance to next round or questionnaire
        if exp.round < ROUNDS_PER_PHASE:
            exp.round += 1
            st.rerun()  # Immediately advance to next round
        else:
            st.session_state['phase_complete'] = True
            st.session_state['step'] = 'questionnaire'
            st.rerun()  # Go to questionnaire

def questionnaire_screen():
    exp = st.session_state['experiment']
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = exp.phase
    responses = post_phase_questionnaire(actual_phase)
    # Store the current responses in session state for the callback
    st.session_state['current_questionnaire_responses'] = responses
    st.button('Submit Questionnaire & Start Next Phase', on_click=submit_questionnaire)

def debrief_screen():
    st.subheader("Debrief and Final Feedback")
    st.markdown("Thank you for participating! Please answer a few final questions about your overall experience.")
    feedback = debrief_questionnaire()
    # Store debrief responses for callback
    st.session_state['current_debrief_responses'] = feedback

    if not st.session_state.get('final_submission_complete', False):
        st.button('Submit Final Feedback & Complete Experiment', on_click=submit_debrief_callback)
    else:
        st.success("✅ Your responses have been submitted successfully!")
        st.button('Continue to Thank You', on_click=lambda: st.session_state.update({'step': 'thank_you'}))

def exit_screen():
    st.subheader("Experiment Exited")
    st.markdown(f"You have exited the experiment at {st.session_state['exit_time']}.")
    st.markdown("If you exited by mistake, you may restart below.")
    st.button('Restart', on_click=restart_experiment)
    if st.session_state.get('restart_clicked'):
        init_session()
        st.session_state['restart_clicked'] = False

def thank_you_screen():
    st.subheader("Thank you for your participation!")
    st.markdown("You have completed all phases. Your data has been saved. ")
    st.button('Restart', on_click=restart_experiment)
    if st.session_state.get('restart_clicked'):
        init_session()
        st.session_state['restart_clicked'] = False

# Main app flow
if st.session_state['step'] == 'welcome':
    welcome_screen()
elif st.session_state['step'] == 'enter_id':
    id_screen()
elif st.session_state['step'] == 'instructions':
    instructions_screen()
elif st.session_state['step'] == 'rounds':
    rounds_screen()
elif st.session_state['step'] == 'questionnaire':
    questionnaire_screen()
elif st.session_state['step'] == 'debrief':
    debrief_screen()
elif st.session_state['step'] == 'exit_screen':
    exit_screen()
elif st.session_state['step'] == 'thank_you':
    thank_you_screen()
