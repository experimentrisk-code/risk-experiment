import pandas as pd
import os
import time
from constants import DATA_FILE

# Google Sheets integration
import streamlit as st
from streamlit_gsheets import GSheetsConnection

GOOGLE_SHEET_FILE = 'my_experiment_data'  # Name of the Google Sheets file
RESULTS_SHEET = 'Results'
QUESTIONNAIRES_SHEET = 'Questionnaires'

QUESTIONNAIRE_HEADER = [
    'session_id', 'participant_id', 'professional_area', 'phase',
    'reason', 'pattern', 'stress', 'confidence', 'perceived_control', 'strategy',
    'overall_stress', 'overall_confidence', 'phase_preference', 'final_strategy', 'comments'
]

def get_gsheet_worksheet(sheet_name):
    # This function is no longer used with GSheetsConnection
    raise NotImplementedError("get_gsheet_worksheet is replaced by gsheets_conn().append")

# Create and cache a GSheets connection resource
@st.cache_resource
def gsheets_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def append_dataframe_to_sheet(df, worksheet):
    """
    Append rows by reading existing data, concatenating, and updating the worksheet.
    Uses ttl="0" to avoid cache. Aligns columns to the union of existing and new.
    """
    try:
        conn = gsheets_conn()
        existing_df = conn.read(worksheet=worksheet, ttl="0")
        if not isinstance(existing_df, pd.DataFrame) or existing_df is None:
            existing_df = pd.DataFrame()

        # Determine unified columns (preserve existing order, then add any new columns)
        existing_cols = list(existing_df.columns) if not existing_df.empty else []
        new_cols = [c for c in df.columns if c not in existing_cols]
        unified_cols = existing_cols + new_cols if existing_cols else list(df.columns)

        # Reindex both frames to unified columns
        existing_aligned = existing_df.reindex(columns=unified_cols, fill_value="") if not existing_df.empty else pd.DataFrame(columns=unified_cols)
        new_aligned = df.reindex(columns=unified_cols, fill_value="")

        combined = pd.concat([existing_aligned, new_aligned], ignore_index=True)
        conn.update(worksheet=worksheet, data=combined)
    except Exception as e:
        print(f"GSheetsConnection error appending to {worksheet}: {e}")

def save_rows_to_gsheet_worksheet(sheet_name, rows, header=None):
    # No longer needed when using GSheetsConnection directly
    pass

# Test function for Google Sheets integration
def test_gsheet():
    try:
        save_rows_to_gsheet_worksheet(RESULTS_SHEET, [[
            'test_id', 'test_area', 'test_phase', 'test_round', 'test_box', 'test_time', 'test_result', 'test_reward', 'test_earnings', 'test_p_safe', 'test_p_uncertain', 'test_init_p_safe', 'test_init_p_uncertain'
        ]], header=[
            'participant_id', 'professional_area', 'phase', 'round', 'box_chosen', 'decision_time',
            'result', 'reward', 'cumulative_earnings', 'p_safe', 'p_uncertain',
            'init_p_safe', 'init_p_uncertain'
        ])
        save_rows_to_gsheet_worksheet(QUESTIONNAIRES_SHEET, [[
            'test_id', 'test_area', 'test_phase', '', '', '', '', '', '', '', '', '', ''
        ]], header=QUESTIONNAIRE_HEADER)
        print('Google Sheets test rows appended successfully.')
    except Exception as e:
        print(f'Google Sheets integration failed: {e}')

# Save all phase results to a single CSV file for all participants
def save_round_data(data, participant_id, initial_probs=None, seeds=None):
    if not data or not participant_id:
        raise ValueError("No data or participant ID provided for saving.")
    filename = 'experiment_data_all.csv'
    # Build per-phase init probabilities map
    init_map = initial_probs if isinstance(initial_probs, dict) else {}
    # Append init probs per row based on the row's phase (index 2)
    data_with_init = []
    for row in data:
        try:
            row_phase = row[2]  # after adding session_id, indexes shift below; adjust later if needed
        except IndexError:
            row_phase = None
        phase_inits = init_map.get(row_phase, {}) if row_phase is not None else {}
        init_p_safe = phase_inits.get('p_safe', None)
        init_p_uncertain = phase_inits.get('p_uncertain', None)
        data_with_init.append(row + [init_p_safe, init_p_uncertain])
    df = pd.DataFrame(data_with_init, columns=[
        'session_id', 'participant_id', 'professional_area', 'phase', 'round', 'box_chosen', 'decision_time',
        'result', 'reward', 'cumulative_earnings', 'p_safe', 'p_uncertain',
        'init_p_safe', 'init_p_uncertain'
    ])
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.stat(filename).st_size == 0
    df.to_csv(filename, mode='a', header=write_header, index=False)
    # Append to Google Sheets via append-only helper
    append_dataframe_to_sheet(df, worksheet=RESULTS_SHEET)

def get_unique_filename(base, participant_id):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return f"{base}_pid{participant_id}_{timestamp}.csv"

def save_questionnaire(participant_id, phase, responses):
    if not participant_id or not responses:
        raise ValueError("Missing participant ID or responses for questionnaire.")
    
    filename = 'questionnaire_data_all.csv'
    
    # Handle batch processing (when responses is a list of questionnaire entries)
    if phase == 'batch' and isinstance(responses, list):
        # Process multiple questionnaire entries at once
        rows_data = []
        for entry in responses:
            # Fill all possible columns, missing values as blank
            row_dict = {col: '' for col in QUESTIONNAIRE_HEADER}
            row_dict['participant_id'] = entry.get('participant_id', participant_id)
            row_dict['phase'] = entry.get('phase', '')
            # Copy all other fields from the entry
            for k, v in entry.items():
                if k in QUESTIONNAIRE_HEADER:
                    row_dict[k] = v
            rows_data.append(row_dict)
        
        # Create DataFrame with all entries
        df = pd.DataFrame(rows_data, columns=QUESTIONNAIRE_HEADER)
        
        # Prepare data for Google Sheets
        gsheet_rows = [list(row.values()) for row in rows_data]
    else:
        # Handle single entry (legacy support)
        row_dict = {col: '' for col in QUESTIONNAIRE_HEADER}
        row_dict['participant_id'] = participant_id
        row_dict['phase'] = phase
        for k, v in responses.items():
            if k in QUESTIONNAIRE_HEADER:
                row_dict[k] = v
        df = pd.DataFrame([row_dict], columns=QUESTIONNAIRE_HEADER)
        gsheet_rows = [list(row_dict.values())]
    
    # Save to CSV
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.stat(filename).st_size == 0
    df.to_csv(filename, mode='a', header=write_header, index=False)
    # Append to Google Sheets via append-only helper
    append_dataframe_to_sheet(df, worksheet=QUESTIONNAIRES_SHEET)

# Test function to verify data is sent to Google Sheets
def test_send_data_to_gsheet():
    """
    Append test rows to both sheets and verify by reading them back (no cache).
    """
    import random
    import string

    # Unique test id to find appended rows
    test_id = 'test_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Results test df
    results_df = pd.DataFrame([
        [
            test_id, 'TestParticipant', 'TestArea', '1', '1', 'A', '1.23', 'red', '5', '5', '0.5', '0.5', '0.5', '0.5'
        ]
    ], columns=[
        'session_id', 'participant_id', 'professional_area', 'phase', 'round', 'box_chosen', 'decision_time',
        'result', 'reward', 'cumulative_earnings', 'p_safe', 'p_uncertain',
        'init_p_safe', 'init_p_uncertain'
    ])

    # Questionnaire test df
    questionnaire_df = pd.DataFrame([
        [
            test_id, test_id, 'TestArea', '1', 'reason', 'pattern', '3', '4', '5', 'strategy',
            '2', '3', '1', 'final_strategy', 'test_comment'
        ]
    ], columns=QUESTIONNAIRE_HEADER)

    # Append
    append_dataframe_to_sheet(results_df, worksheet=RESULTS_SHEET)
    append_dataframe_to_sheet(questionnaire_df, worksheet=QUESTIONNAIRES_SHEET)

    # Verify using fresh reads
    conn = gsheets_conn()
    results_read = conn.read(worksheet=RESULTS_SHEET, ttl="0")
    questionnaire_read = conn.read(worksheet=QUESTIONNAIRES_SHEET, ttl="0")

    assert (results_read['session_id'] == test_id).any(), "Appended Results row not found"
    assert (questionnaire_read['session_id'] == test_id).any(), "Appended Questionnaire row not found"
    print("Google Sheets test PASSED: Append-only writes verified with fresh reads.")
