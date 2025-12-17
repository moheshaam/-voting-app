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
            return {"votes": []}
        
        # Get all values
        all_values = sheet.get_all_values()
        
        if len(all_values) < 1 or not all_values[0][0]:
            return {"votes": []}
        
        # Try to parse JSON from cell A1
        try:
            votes_data = json.loads(all_values[0][0])
            return votes_data
        except:
            return {"votes": []}
    except Exception as e:
        st.error(f"Error loading votes: {e}")
        return {"votes": []}

def save_votes(votes_data):
    """Save votes to Google Sheets"""
    try:
        sheet = get_google_sheet()
        if sheet is None:
            return False
        
        # Clear all data
        sheet.clear()
        
        # Save as JSON in cell A1
        json_data = json.dumps(votes_data, ensure_ascii=False)
        sheet.update('A1', [[json_data]])
        
        return True
    except Exception as e:
        st.error(f"Error saving votes: {e}")
        return False

def get_voter_question_count(votes_data, voter_name):
    """Get the number of questions a voter has answered"""
    count = sum(1 for vote in votes_data["votes"] if vote["voter"] == voter_name)
    return count

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
    st.title("🗳️ نظام التصويت")
    
    # Initialize session state
    if 'voter_name' not in st.session_state:
        st.session_state.voter_name = None
    if 'vote_count' not in st.session_state:
        st.session_state.vote_count = 0
    
    # Load voting data
    votes_data = load_votes()
    
    # Step 1: Ask for name first
    if not st.session_state.voter_name:
        st.markdown("### أدخل اسمك للبدء:")
        voter_name = st.text_input("الاسم", max_chars=50, key="name_input")
        
        if st.button("متابعة", use_container_width=True):
            if voter_name and voter_name.strip():
                st.session_state.voter_name = voter_name.strip()
                st.rerun()
            else:
                st.error("⚠️ من فضلك أدخل اسمك!")
    
    # Step 2: Show voting options after name is entered
    else:
        # Get current question number for this voter
        question_num = get_voter_question_count(votes_data, st.session_state.voter_name) + 1
        
        st.success(f"مرحباً {st.session_state.voter_name}! 👋")
        st.info(f"السؤال رقم {question_num}")
        st.markdown("### اختر إجابتك:")
        
        # Get voting options
        options = ["رقم 1", "رقم 2", "رقم 3", "رقم 4", "غير صحيح"]
        
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
            
            # Add vote to the list
            vote_entry = {
                "voter": st.session_state.voter_name,
                "question": question_num,
                "choice": choice,
                "timestamp": datetime.now().isoformat()
            }
            votes_data["votes"].append(vote_entry)
            
            # Save votes
            save_votes(votes_data)
            
            # Show success message
            st.success(f"✅ تم تسجيل إجابتك للسؤال {question_num}: {choice}")
            
            # Increment vote count to reset radio selection
            st.session_state.vote_count += 1
            st.rerun()
        
        # View results option
        st.markdown("---")
        if st.button("📊 عرض النتائج", use_container_width=True):
            show_results(votes_data)

def show_results(votes_data):
    """Display voting results"""
    st.markdown("## 📊 النتائج الكاملة")
    
    if not votes_data["votes"]:
        st.warning("لا توجد أصوات بعد")
        return
    
    # Get all unique question numbers
    questions = sorted(set(vote["question"] for vote in votes_data["votes"]))
    
    for q_num in questions:
        st.markdown(f"### السؤال رقم {q_num}")
        
        # Get all votes for this question
        question_votes = [v for v in votes_data["votes"] if v["question"] == q_num]
        total_votes = len(question_votes)
        
        st.info(f"إجمالي الأصوات: {total_votes}")
        
        # Group by choice
        options = ["رقم 1", "رقم 2", "رقم 3", "رقم 4", "غير صحيح"]
        
        for option in options:
            option_votes = [v for v in question_votes if v["choice"] == option]
            count = len(option_votes)
            
            if count > 0:
                percentage = (count / total_votes * 100) if total_votes > 0 else 0
                
                st.markdown(f"**{option}**")
                st.progress(percentage / 100)
                st.markdown(f"{count} أصوات ({percentage:.1f}%)")
                
                # Show voters
                voters = [v["voter"] for v in option_votes]
                voters_str = ", ".join(voters)
                st.markdown(f"🗳️ المصوتون: {voters_str}")
                st.markdown("")
        
        st.markdown("---")
    
    # Refresh button
    if st.button("🔄 تحديث النتائج", use_container_width=True):
        st.rerun()

# Admin panel (optional)
def admin_panel():
    st.sidebar.title("⚙️ Admin Panel")
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":  # Change this password!
        st.sidebar.success("Admin access granted")
        
        if st.sidebar.button("Reset All Votes"):
            votes_data = {"votes": []}
            save_votes(votes_data)
            st.sidebar.success("Votes reset!")
            st.rerun()
        
        if st.sidebar.button("Clear My Session"):
            st.session_state.voter_name = None
            st.session_state.vote_count = 0
            st.rerun()

if __name__ == "__main__":
    admin_panel()
    main()
