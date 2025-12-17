from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from supabase import create_client
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Supabase configuration
SUPABASE_URL = "https://gsastznmljkrimykccom.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYXN0em5tbGprcmlteWtjY29tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5OTkyOTYsImV4cCI6MjA4MTU3NTI5Nn0.KxcwthJhLFJGEY97-hMFGv8dkh6N92whJFzHn0h6Rd0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

OPTIONS = [
    "(1) أحمد جعفر",
    "(2) عزت عبدالرحمن",
    "(3) أحمد رجب الشافعي",
    "(4) يونس عبد الرازق"
]

@app.route('/')
def index():
    if 'voter_name' not in session:
        return render_template('login.html')
    return redirect(url_for('vote'))

@app.route('/login', methods=['POST'])
def login():
    voter_name = request.form.get('voter_name', '').strip()
    if voter_name:
        session['voter_name'] = voter_name
        session['current_question'] = 1
    return redirect(url_for('vote'))

@app.route('/vote')
def vote():
    if 'voter_name' not in session:
        return redirect(url_for('index'))
    
    voter_name = session['voter_name']
    current_q = session.get('current_question', 1)
    
    # Get voter's total votes
    response = supabase.table('votes').select('*').eq('voter', voter_name).execute()
    total_votes = len(response.data) if response.data else 0
    
    return render_template('vote.html', 
                         voter_name=voter_name, 
                         current_question=current_q,
                         total_votes=total_votes,
                         options=OPTIONS)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if 'voter_name' not in session:
        return redirect(url_for('index'))
    
    voter_name = session['voter_name']
    choice = request.form.get('choice')
    current_q = session.get('current_question', 1)
    
    if choice:
        # Save vote
        vote_entry = {
            "voter": voter_name,
            "question": current_q,
            "choice": choice,
            "timestamp": datetime.now().isoformat()
        }
        supabase.table('votes').insert(vote_entry).execute()
        
        # Move to next question
        session['current_question'] = current_q + 1
    
    return redirect(url_for('vote'))

@app.route('/results')
def results():
    if 'voter_name' not in session:
        return redirect(url_for('index'))
    
    voter_name = session['voter_name']
    response = supabase.table('votes').select('*').eq('voter', voter_name).execute()
    votes = response.data if response.data else []
    
    # Group by question
    votes_by_q = {}
    for vote in votes:
        q = vote['question']
        if q not in votes_by_q:
            votes_by_q[q] = []
        votes_by_q[q].append(vote['choice'])
    
    return render_template('results.html', 
                         voter_name=voter_name,
                         votes_by_q=votes_by_q,
                         total_votes=len(votes))

@app.route('/admin')
def admin():
    password = request.args.get('password', '')
    if password != 'admin123':
        return render_template('admin_login.html')
    
    # Get all votes
    response = supabase.table('votes').select('*').execute()
    all_votes = response.data if response.data else []
    
    # Group by question
    votes_by_q = {}
    for vote in all_votes:
        q = vote['question']
        if q not in votes_by_q:
            votes_by_q[q] = {}
        choice = vote['choice']
        votes_by_q[q][choice] = votes_by_q[q].get(choice, 0) + 1
    
    return render_template('admin.html', votes_by_q=votes_by_q)

@app.route('/reset_votes', methods=['POST'])
def reset_votes():
    password = request.form.get('password', '')
    if password == 'admin123':
        supabase.table('votes').delete().neq('id', 0).execute()
    return redirect(url_for('admin', password='admin123'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
