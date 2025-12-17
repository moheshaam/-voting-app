import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# Google Sheets configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

@st.cache_resource
def get_google_sheet():
    """Connect to Google Sheets using credentials from Streamlit secrets"""
    try:
        # Get credentials from Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet (you'll need to create this and share it with the service account)
        sheet = client.open("Voting_App_Data").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def load_votes():
    """Load votes from Google Sheets"""
    try:
        sheet = get_google_sheet()
        if sheet is None:
            return {"options": {}, "voters": [], "total_votes": 0}
        
        # Get all values
        all_values = sheet.get_all_values()
        
        if len(all_values) < 2:
            # Initialize sheet if empty
            return {"options": {}, "voters": [], "total_votes": 0}
        
        # Parse the data
        # Row format: Column A = Option name, Column B = Vote count, Column D = Voters (comma-separated)
        votes_data = {"options": {}, "voters": [], "total_votes": 0}
        
        # Read options from rows 2-5 (indices 1-4)
        for i in range(1, min(len(all_values), 6)):  # Rows 2-6
            row = all_values[i]
            if len(row) >= 2 and row[0]:  # Column D (index 3)
                option_name = row[0]
                vote_count = int(row[1]) if row[1] and row[1].isdigit() else 0
                votes_data["options"][option_name] = vote_count
        
        # Read voters from column D, row 2 (all voters in one cell, comma-separated)
        if len(all_values) > 1 and len(all_values[1]) > 3 and all_values[1][3]:
            voters_str = all_values[1][3]
            votes_data["voters"] = [v.strip() for v in voters_str.split(',') if v.strip()]
        
        votes_data["total_votes"] = len(votes_data["voters"])
        return votes_data
    except Exception as e:
        st.error(f"Error loading votes: {e}")
        return {"options": {}, "voters": [], "total_votes": 0}

def save_votes(votes_data):
    """Save votes to Google Sheets"""
    try:
        sheet = get_google_sheet()
        if sheet is None:
            return False
        
        # Clear all data
        sheet.clear()
        
        # Row 1: Headers
        sheet.update('A1:D1', [['Option', 'Votes', '', 'Voters']])
        
        # Rows 2-5: Options and vote counts
        options_list = list(votes_data["options"].items())
        for i, (option, count) in enumerate(options_list, start=2):
            # Put voters list only in the first row (D2)
            if i == 2:
                voters_str = ','.join(votes_data["voters"]) if votes_data["voters"] else ''
                sheet.update(f'A{i}:D{i}', [[option, count, '', voters_str]])
            else:
                sheet.update(f'A{i}:B{i}', [[option, count]])
        
        return True
    except Exception as e:
        st.error(f"Error saving votes: {e}")
        return False

def initialize_voting_options():
    """Initialize voting options if not set"""
    votes_data = load_votes()
    if not votes_data["options"]:
        # Default voting options - customize as needed
        votes_data["options"] = {
            "رقم 1": 0,
            "رقم 2": 0,
            "رقم 3": 0,
            "رقم 4": 0,
            "غير صحيح": 0
        }
        votes_data["voters"] = []
        votes_data["total_votes"] = 0
        save_votes(votes_data)
    return votes_data

# Mobile-friendly page configuration
st.set_page_config(
    page_title="Voting App",
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization
st.markdown("""
    <style>
    /* Mobile-friendly styles */
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        margin: 10px 0;
        border-radius: 10px;
    }
    
    .stRadio > div {
        font-size: 18px;
    }
    
    .stRadio > div > label {
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #f0f2f6;
        border-radius: 10px;
        display: block;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .stRadio > div > label:hover {
        border-color: #ff4b4b;
        background-color: #f0f2f6;
    }
    
    h1 {
        text-align: center;
        color: #ff4b4b;
    }
    
    .vote-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Touch-friendly spacing */
    @media (max-width: 768px) {
        .stButton > button {
            height: 70px;
            font-size: 20px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Main app
def main():
    st.title("🗳️ Voting Form")
    
    # Initialize session state
    if 'voter_name' not in st.session_state:
        st.session_state.voter_name = None
    if 'show_voting' not in st.session_state:
        st.session_state.show_voting = False
    if 'vote_count' not in st.session_state:
        st.session_state.vote_count = 0
    
    # Initialize voting data
    votes_data = initialize_voting_options()
    
    # Step 1: Ask for name first
    if not st.session_state.voter_name:
        st.markdown("### أدخل اسمك للبدء:")
        voter_name = st.text_input("الاسم", max_chars=50, key="name_input")
        
        if st.button("متابعة", use_container_width=True):
            if voter_name and voter_name.strip():
                st.session_state.voter_name = voter_name.strip()
                st.session_state.show_voting = True
                st.rerun()
            else:
                st.error("⚠️ من فضلك أدخل اسمك!")
    
    # Step 2: Show voting options after name is entered
    else:
        st.success(f"مرحباً {st.session_state.voter_name}! 👋")
        st.markdown("### اختر خيارك:")
        
        # Get voting options
        options = list(votes_data["options"].keys())
        
        # Radio buttons for voting - immediate voting on selection
        choice = st.radio(
            "اختر رقم:",
            options,
            index=None,
            label_visibility="collapsed",
            key=f"vote_radio_{st.session_state.vote_count}"
        )
        
        # Immediate voting when choice is made
        if choice is not None:
            # Record vote immediately
            votes_data = load_votes()
            
            # Record vote
            if choice in votes_data["options"]:
                votes_data["options"][choice] += 1
            else:
                votes_data["options"][choice] = 1
            
            # Add voter to list with timestamp to allow multiple votes
            voter_entry = f"{st.session_state.voter_name}_{int(datetime.now().timestamp())}"
            votes_data["voters"].append(voter_entry)
            votes_data["total_votes"] = len(votes_data["voters"])
            
            # Save votes
            save_votes(votes_data)
            
            # Show success message
            st.success(f"✅ تم تسجيل صوتك للخيار: {choice}")
            
            # Increment vote count to reset radio selection
            st.session_state.vote_count += 1
            st.rerun()
        
        # View results option
        st.markdown("---")
        if st.button("📊 عرض النتائج", use_container_width=True):
            show_results(votes_data)
        
        # Option to change name
        if st.button("🔄 تغيير الاسم", use_container_width=True):
            st.session_state.voter_name = None
            st.session_state.show_voting = False
            st.rerun()

def show_results(votes_data):
    """Display voting results"""
    st.markdown("### 📊 Current Results")
    
    total_votes = votes_data["total_votes"]
    st.info(f"Total Votes: {total_votes}")
    
    if total_votes > 0:
        for option, count in votes_data["options"].items():
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            st.markdown(f"**{option}**")
            st.progress(percentage / 100)
            st.markdown(f"{count} votes ({percentage:.1f}%)")
            st.markdown("")
    else:
        st.warning("No votes recorded yet.")
    
    # Refresh button
    if st.button("🔄 Refresh Results", use_container_width=True):
        st.rerun()

# Admin panel (optional)
def admin_panel():
    st.sidebar.title("⚙️ Admin Panel")
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":  # Change this password!
        st.sidebar.success("Admin access granted")
        
        if st.sidebar.button("Reset All Votes"):
            votes_data = {
                "options": {
                    "رقم 1": 0,
                    "رقم 2": 0,
                    "رقم 3": 0,
                    "رقم 4": 0,
                    "غير صحيح": 0
                },
                "voters": [],
                "total_votes": 0
            }
            save_votes(votes_data)
            st.sidebar.success("Votes reset!")
            st.rerun()
        
        if st.sidebar.button("Clear My Session"):
            st.session_state.voter_name = None
            st.session_state.show_voting = False
            st.session_state.vote_count = 0
            st.rerun()

if __name__ == "__main__":
    admin_panel()
    main()
