import streamlit as st
from constants import *

def display_boxes(phase, p_safe, p_uncertain, show_special=False):
    """
    Display two boxes with probability visualization using simple HTML/CSS grid
    """
    # Calculate number of colored balls for each box
    safe_balls = int(p_safe * 100)
    uncertain_balls = int(p_uncertain * 100)
    
    # Create HTML for the boxes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Box A**")
        
        # Show different visualizations based on phase
        if phase == 1 or phase == 2:  # Box A is known (risk) - show blue/white balls
            balls_html = "<div style='display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; max-width: 200px;'>"
            for i in range(100):
                color = "#4285f4" if i < safe_balls else "#e0e0e0"  # Blue for winning balls, gray for losing
                balls_html += f"<div style='width: 15px; height: 15px; border-radius: 50%; background-color: {color};'></div>"
            balls_html += "</div>"
            st.markdown(balls_html, unsafe_allow_html=True)
            
            # Show exact probability information for known risk
            info_html = f"""
            <div style='margin-top: 28px; margin-bottom: 32px; padding: 12px 0 12px 0; text-align: center; max-width: 200px; margin-left: 0; margin-right: auto; background: rgba(255,255,255,0.04); border-radius: 12px;'>
                <div style='font-weight: 600;'>{safe_balls}% chance of winning {REWARD_RED}€</div>
                <div style='margin-top: 2px; font-weight: 600;'>{100-safe_balls}% chance of losing {abs(REWARD_BLACK)}€</div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            
        elif phase == 3:  # Box A is unknown (ambiguity) - show question marks
            balls_html = "<div style='display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; max-width: 200px;'>"
            for i in range(100):
                balls_html += "<div style='width: 15px; height: 15px; border-radius: 50%; background-color: #888; color: white; font-size: 8px; text-align: center; line-height: 15px;'>?</div>"
            balls_html += "</div>"
            st.markdown(balls_html, unsafe_allow_html=True)
            
            # Show unknown probability information
            info_html = f"""
            <div style='margin-top: 28px; margin-bottom: 32px; padding: 12px 0 12px 0; text-align: center; max-width: 200px; margin-left: 0; margin-right: auto; background: rgba(255,255,255,0.04); border-radius: 12px;'>
                <div style='font-weight: 600;'>Unknown probability</div>
                <div style='margin-top: 2px; font-size: 1.18em; font-weight: 700;'>Win {AMBIGUITY_REWARD}€ or lose {abs(AMBIGUITY_LOSS)}€</div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Box B**")
        # For unknown probability boxes, show question marks or different visualization based on phase
        if phase == 1:  # Ambiguity - all question marks
            balls_html = "<div style='display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; max-width: 200px;'>"
            for i in range(100):
                balls_html += "<div style='width: 15px; height: 15px; border-radius: 50%; background-color: #888; color: white; font-size: 8px; text-align: center; line-height: 15px;'>?</div>"
            balls_html += "</div>"
            st.markdown(balls_html, unsafe_allow_html=True)
            # Box B information for phase 1 (ambiguity)
            info_html = f"""
            <div style='margin-top: 28px; margin-bottom: 32px; padding: 12px 0 12px 0; text-align: center; max-width: 200px; margin-left: 0; margin-right: auto; background: rgba(255,255,255,0.04); border-radius: 12px;'>
                <div style='font-weight: 600;'>Unknown probability</div>
                <div style='margin-top: 2px; font-size: 1.18em; font-weight: 700;'>Win {AMBIGUITY_REWARD}€ or lose {abs(AMBIGUITY_LOSS)}€</div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            
        elif phase == 2 or phase == 3:  # Rumsfeld - all question marks (no information revealed)
            balls_html = "<div style='display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; max-width: 200px;'>"
            for i in range(100):
                balls_html += "<div style='width: 15px; height: 15px; border-radius: 50%; background-color: #888; color: white; font-size: 8px; text-align: center; line-height: 15px;'>?</div>"
            balls_html += "</div>"
            st.markdown(balls_html, unsafe_allow_html=True)
            # Box B information for phases 2&3 (Rumsfeld uncertainty)
            if phase == 2:
                info_html = f"""
                <div style='margin-top: 28px; margin-bottom: 32px; padding: 12px 0 12px 0; text-align: center; max-width: 200px; margin-left: 0; margin-right: auto; background: rgba(255,255,255,0.04); border-radius: 12px;'>
                    <div style='font-weight: 600;'>Totally different rules might apply</div>
                </div>
                """
                st.markdown(info_html, unsafe_allow_html=True)
                st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            else:  # phase == 3
                info_html = f"""
                <div style='margin-top: 28px; margin-bottom: 32px; padding: 12px 0 12px 0; text-align: center; max-width: 200px; margin-left: 0; margin-right: auto; background: rgba(255,255,255,0.04); border-radius: 12px;'>
                    <div style='font-weight: 600;'>Totally different rules might apply</div>
                </div>
                """
                st.markdown(info_html, unsafe_allow_html=True)
                st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

def show_instructions(phase):
    if phase == 1:
        st.markdown("""
        - **Box A:** Known probability (risk)
        - **Box B:** Unknown probability (ambiguity)
        """)
    elif phase == 2:
        st.markdown("""
        - **Box A:** Known probability (risk)
        - **Box B:** Totally different rules might apply
        """)
    elif phase == 3:
        st.markdown("""
        - **Box A:** Unknown probability (ambiguity)
        - **Box B:** Totally different rules might apply
        """)

def show_feedback(result, reward, box):
    if result == 'red':
        st.success(f"You drew a red ball from Box {box} (+{reward} €)")
    elif result == 'black':
        st.error(f"You drew a black ball from Box {box} ({reward} €)")
    elif result == 'gold':
        st.success(f"Surprise! You drew a gold ball from Box {box} (+{reward} €)")
    elif result == 'silver':
        st.warning(f"Surprise! You drew a silver ball from Box {box} ({reward} €)")
