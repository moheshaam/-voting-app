# 🗳️ Streamlit Voting App (Cloud Edition)

A mobile-friendly voting application built with Streamlit that uses **Google Sheets** for cloud-based vote synchronization - perfect for Streamlit Cloud deployment!

## Features

- ✅ Mobile-optimized responsive design
- ☁️ **Cloud storage with Google Sheets** - works on Streamlit Cloud
- 🔄 Real-time vote synchronization across all devices
- 🔒 One vote per user (tracked by session)
- 📊 Live results display with percentages
- ⚙️ Admin panel for vote management
- 📱 Touch-friendly interface for mobile devices
- 🌍 Accessible from anywhere - no local server needed!

## Quick Start (Local Testing)

1. **Follow the setup guide:** Open `SETUP_GUIDE.md` for detailed instructions
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Google Sheets credentials** in `.streamlit/secrets.toml`
4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Deployment to Streamlit Cloud

See `SETUP_GUIDE.md` for complete deployment instructions including:
- Google Cloud setup
- Service Account creation
- Google Sheets configuration
- Streamlit Cloud deployment

## How It Works

- **Storage:** Votes are stored in a Google Sheets spreadsheet
- **Synchronization:** All users see the same data in real-time
- **Security:** Uses Google Service Account for secure API access
- **Scalability:** Works for multiple concurrent voters
- **Persistence:** Data is never lost (stored in the cloud)

## Files

- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `.streamlit/secrets.toml` - Google credentials (not committed to git)
- `SETUP_GUIDE.md` - Detailed setup instructions in Arabic
- `.gitignore` - Excludes secrets from version control

## Customization

Edit the `initialize_voting_options()` function in `app.py` to change voting options.

## Tech Stack

- **Streamlit** - Web framework
- **Google Sheets API** - Cloud storage
- **gspread** - Python library for Google Sheets
- **Google Auth** - Authentication

## Notes

- Free to use with Google Sheets (no database costs!)
- Works on Streamlit Cloud free tier
- Mobile-optimized for easy voting on phones
- No server maintenance required
