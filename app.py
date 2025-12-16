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
        
        # Parse the data (expecting: Option, Count in columns A-B, and voters in column D)
        votes_data = {"options": {}, "voters": [], "total_votes": 0}
        
        for row in all_values[1:]:  # Skip header
            if len(row) >= 2 and row[0]:
                votes_data["options"][row[0]] = int(row[1]) if row[1].isdigit() else 0
            if len(row) >= 4 and row[3]:  # Voters in column D
                votes_data["voters"] = row[3].split(',') if row[3] else []
        
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
        
        # Clear existing data
        sheet.clear()
        
        # Prepare data for sheet
        headers = ['Option', 'Votes', '', 'Voters']
        sheet.append_row(headers)
        
        # Add vote counts
        for option, count in votes_data["options"].items():
            voters_str = ','.join(votes_data["voters"]) if votes_data["voters"] else ''
            sheet.append_row([option, count, '', voters_str if option == list(votes_data["options"].keys())[0] else ''])
        
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
            "Option A": 0,
            "Option B": 0,
            "Option C": 0,
            "Option D": 0
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
    if 'voted' not in st.session_state:
        st.session_state.voted = False
    if 'voter_id' not in st.session_state:
        st.session_state.voter_id = None
    
    # Initialize voting data
    votes_data = initialize_voting_options()
    
    # Check if user already voted
    voter_id = st.session_state.voter_id
    
    if st.session_state.voted and voter_id in votes_data.get("voters", []):
        st.success("✅ Thank you! Your vote has been recorded.")
        st.info("You have already voted in this poll.")
        
        # Show results button
        if st.button("📊 View Results", use_container_width=True):
            show_results(votes_data)
    else:
        st.markdown("### Please select your choice:")
        
        # Voting form
        with st.form("voting_form"):
            # Get voting options
            options = list(votes_data["options"].keys())
            
            # Radio buttons for voting
            choice = st.radio(
                "Choose one option:",
                options,
                index=None,
                label_visibility="collapsed"
            )
            
            # Voter identification (simple approach - can be enhanced)
            voter_name = st.text_input("Your Name (Optional)", max_chars=50)
            
            # Submit button
            submitted = st.form_submit_button("🗳️ Submit Vote", use_container_width=True)
            
            if submitted:
                if choice is None:
                    st.error("⚠️ Please select an option before submitting!")
                else:
                    # Generate voter ID
                    if not voter_id:
                        voter_id = f"{datetime.now().timestamp()}_{hash(voter_name) if voter_name else 'anonymous'}"
                        st.session_state.voter_id = voter_id
                    
                    # Reload votes to get latest data
                    votes_data = load_votes()
                    
                    # Check if already voted
                    if voter_id not in votes_data["voters"]:
                        # Record vote
                        if choice in votes_data["options"]:
                            votes_data["options"][choice] += 1
                        else:
                            # Initialize option if not exists
                            votes_data["options"][choice] = 1
                        
                        votes_data["voters"].append(voter_id)
                        votes_data["total_votes"] = len(votes_data["voters"])
                        
                        # Save synchronized votes
                        save_votes(votes_data)
                        
                        st.session_state.voted = True
                        st.rerun()
                    else:
                        st.error("You have already voted!")
        
        # View results option
        st.markdown("---")
        if st.button("📊 View Current Results", use_container_width=True):
            show_results(votes_data)

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
                    "Option A": 0,
                    "Option B": 0,
                    "Option C": 0,
                    "Option D": 0
                },
                "voters": [],
                "total_votes": 0
            }
            save_votes(votes_data)
            st.sidebar.success("Votes reset!")
            st.rerun()
        
        if st.sidebar.button("Clear My Vote"):
            st.session_state.voted = False
            st.session_state.voter_id = None
            st.rerun()

if __name__ == "__main__":
    admin_panel()
    main()
