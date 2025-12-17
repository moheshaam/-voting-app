import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://gsastznmljkrimykccom.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYXN0em5tbGprcmlteWtjY29tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5OTkyOTYsImV4cCI6MjA4MTU3NTI5Nn0.KxcwthJhLFJGEY97-hMFGv8dkh6N92whJFzHn0h6Rd0"

@st.cache_resource
def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_votes():
    """Load votes from Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('votes').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        # Return empty list on error
        return []

def save_vote(voter_name, question_num, choice):
    """Save a single vote to Supabase"""
    try:
        supabase = get_supabase_client()
        vote_entry = {
            "voter": voter_name,
            "question": question_num,
            "choice": choice,
            "timestamp": datetime.now().isoformat()
        }
        supabase.table('votes').insert(vote_entry).execute()
        return True
    except Exception as e:
        return False

def save_votes_batch(votes_list):
    """Save multiple votes to Supabase at once"""
    try:
        supabase = get_supabase_client()
        supabase.table('votes').insert(votes_list).execute()
        return True
    except Exception as e:
        return False

def get_voter_question_count(votes_data, voter_name):
    """Get the number of questions a voter has answered"""
    count = sum(1 for vote in votes_data if vote.get("voter") == voter_name)
    return count

def on_vote_change():
    """Callback function when vote selection changes"""
    # Get the selected choice from session state
    choice_key = f"vote_radio_{st.session_state.widget_key}"
    if choice_key in st.session_state and st.session_state[choice_key] is not None:
        choice = st.session_state[choice_key]
        question_num = st.session_state.current_question
        
        # Check if this vote was already recorded
        if st.session_state.last_saved_question != question_num:
            # Store vote in pending list (batch mode)
            if 'pending_votes' not in st.session_state:
                st.session_state.pending_votes = []
            
            vote_entry = {
                "voter": st.session_state.voter_name,
                "question": question_num,
                "choice": choice,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.pending_votes.append(vote_entry)
            
            # Save every 5 votes or immediately
            if len(st.session_state.pending_votes) >= 5:
                # Save batch
                save_votes_batch(st.session_state.pending_votes)
                st.session_state.pending_votes = []
            else:
                # Save immediately for responsiveness
                save_vote(st.session_state.voter_name, question_num, choice)
            
            # Mark as saved and move to next question
            st.session_state.last_saved_question = question_num
            st.session_state.current_question = question_num + 1
            st.session_state.widget_key += 1

def show_personal_results(votes_data, voter_name):
    """Display personal voting results for a specific voter"""
    st.markdown("## 📋 نتائجك الشخصية")
    
    # Get all votes for this voter (including pending)
    saved_votes = [v for v in votes_data if v.get("voter") == voter_name]
    
    # Add pending votes if any
    pending = []
    if 'pending_votes' in st.session_state:
        pending = st.session_state.pending_votes
    
    total_votes = len(saved_votes) + len(pending)
    
    if total_votes == 0:
        st.info("لم تقم بالتصويت بعد")
        return
    
    st.info(f"إجمالي الأسئلة: {total_votes} سؤال")
    
    # Count votes per choice (saved + pending)
    all_votes = saved_votes + pending
    choice_counts = {}
    for vote in all_votes:
        choice = vote.get("choice")
        if choice:
            choice_counts[choice] = choice_counts.get(choice, 0) + 1
    
    # Display summary
    st.markdown("### ملخص اختياراتك:")
    st.markdown("---")
    
    # Define all options
    all_options = [
        "(1) أحمد جعفر",
        "(2) عزت عبدالرحمن",
        "(3) أحمد رجب الشافعي",
        "(4) يونس عبد الرازق"
    ]
    
    for option in all_options:
        count = choice_counts.get(option, 0)
        if count > 0:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{option}**")
            with col2:
                st.markdown(f"🗳️ **{count} مرة**")
    
    st.markdown("---")

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
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 1
    if 'last_saved_question' not in st.session_state:
        st.session_state.last_saved_question = 0
    if 'widget_key' not in st.session_state:
        st.session_state.widget_key = 0
    
    # Load voting data only once at the beginning
    if 'votes_loaded' not in st.session_state:
        votes_data = load_votes()
        st.session_state.votes_loaded = True
    
    # Step 1: Ask for name first
    if not st.session_state.voter_name:
        st.markdown("### أدخل اسمك للبدء:")
        voter_name = st.text_input("الاسم", max_chars=50, key="name_input")
        
        if st.button("متابعة", use_container_width=True):
            if voter_name and voter_name.strip():
                st.session_state.voter_name = voter_name.strip()
                # Load existing votes for this voter to set correct question number
                votes_data = load_votes()
                existing_count = get_voter_question_count(votes_data, voter_name.strip())
                st.session_state.current_question = existing_count + 1
                st.session_state.pending_votes = []  # Initialize pending votes
                st.rerun()
            else:
                st.error("⚠️ من فضلك أدخل اسمك!")
    
    # Step 2: Show voting options after name is entered
    else:
        question_num = st.session_state.current_question
        
        st.success(f"مرحباً {st.session_state.voter_name}! 👋")
        st.info(f"السؤال رقم {question_num}")
        st.markdown("### اختر إجابتك:")
        
        # Get voting options
        options = [
            "(1) أحمد جعفر",
            "(2) عزت عبدالرحمن",
            "(3) أحمد رجب الشافعي",
            "(4) يونس عبد الرازق"
        ]
        
        # Radio buttons with callback for automatic voting
        choice = st.radio(
            "اختر رقم:",
            options,
            index=None,
            label_visibility="collapsed",
            key=f"vote_radio_{st.session_state.widget_key}",
            on_change=on_vote_change
        )
        
        # Show success message if vote was just saved
        if st.session_state.last_saved_question == question_num - 1:
            st.success(f"✅ تم تسجيل السؤال {question_num - 1}")
        
        # Show pending votes count
        if 'pending_votes' in st.session_state and len(st.session_state.pending_votes) > 0:
            st.info(f"📝 في انتظار الحفظ: {len(st.session_state.pending_votes)} أسئلة")
        
        # Show personal results
        st.markdown("---")
        # Only reload votes when showing results - use cached data
        if 'cached_votes' not in st.session_state or question_num % 10 == 1:
            st.session_state.cached_votes = load_votes()
        show_personal_results(st.session_state.cached_votes, st.session_state.voter_name)

def show_all_results(votes_data):
    """Display all voting results - Admin only"""
    st.markdown("## 📊 النتائج الكاملة (للجميع)")
    
    if not votes_data:
        st.warning("لا توجد أصوات بعد")
        return
    
    # Get all unique question numbers
    questions = sorted(set(vote.get("question", 0) for vote in votes_data if vote.get("question")))
    
    for q_num in questions:
        st.markdown(f"### السؤال رقم {q_num}")
        
        # Get all votes for this question
        question_votes = [v for v in votes_data if v.get("question") == q_num]
        total_votes = len(question_votes)
        
        st.info(f"إجمالي الأصوات: {total_votes}")
        
        # Group by choice
        options = [
            "(1) أحمد جعفر",
            "(2) عزت عبدالرحمن",
            "(3) أحمد رجب الشافعي",
            "(4) يونس عبد الرازق"
        ]
        
        for option in options:
            option_votes = [v for v in question_votes if v.get("choice") == option]
            count = len(option_votes)
            
            if count > 0:
                percentage = (count / total_votes * 100) if total_votes > 0 else 0
                
                st.markdown(f"**{option}**")
                st.progress(percentage / 100)
                st.markdown(f"{count} أصوات ({percentage:.1f}%)")
                
                # Show voters
                voters = [v.get("voter") for v in option_votes if v.get("voter")]
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
        
        # Show all results button
        if st.sidebar.button("📊 عرض نتائج الجميع"):
            votes_data = load_votes()
            show_all_results(votes_data)
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("Reset All Votes"):
            try:
                supabase = get_supabase_client()
                # Delete all votes
                supabase.table('votes').delete().neq('id', 0).execute()
                st.sidebar.success("Votes reset!")
                st.rerun()
            except:
                st.sidebar.error("Error resetting votes")
        
        if st.sidebar.button("Clear My Session"):
            st.session_state.voter_name = None
            st.session_state.current_question = 1
            st.session_state.widget_key = 0
            if 'pending_votes' in st.session_state:
                st.session_state.pending_votes = []
            st.rerun()

if __name__ == "__main__":
    admin_panel()
    main()
