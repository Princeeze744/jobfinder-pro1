"""
JobFinder Pro - AI-Powered Job Application Automation
UPGRADED: Hybrid Mode + CV Attachments
"""

import streamlit as st
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.main import TalentAcquisitionEngine
from src.modules.location_matcher import LocationMatcher
from src.modules.application_tracker import ApplicationTracker
from src.modules.email_sender import EmailSender

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JobFinder Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .verified-badge {
        background: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .ai-badge {
        background: #f59e0b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'engine' not in st.session_state:
    st.session_state.engine = TalentAcquisitionEngine()

if 'location_matcher' not in st.session_state:
    st.session_state.location_matcher = LocationMatcher()

if 'tracker' not in st.session_state:
    st.session_state.tracker = ApplicationTracker()

if 'results' not in st.session_state:
    st.session_state.results = None

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'sender_email' not in st.session_state:
    st.session_state.sender_email = ""

if 'sender_password' not in st.session_state:
    st.session_state.sender_password = ""

if 'uploaded_cv_path' not in st.session_state:
    st.session_state.uploaded_cv_path = None

# ============================================================
# HEADER
# ============================================================

st.markdown("""
    <div style='text-align: center; padding: 30px 0;'>
        <h1>🎯 JobFinder Pro</h1>
        <p style='font-size: 18px; color: #666;'>
            AI-Powered Job Application Automation | Find Companies • Generate Emails • Track Applications
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# SIDEBAR - CONFIGURATION & SETTINGS
# ============================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Email Configuration
    with st.expander("📧 Email Configuration", expanded=False):
        st.markdown("**Configure your Gmail for sending emails**")
        sender_email = st.text_input(
            "Gmail Address:",
            value="trade2uwin@gmail.com",
            help="Your Gmail address"
        )
        sender_password = st.text_input(
            "App Password:",
            type="password",
            help="Gmail App Password (16 characters, no spaces)"
        )
        
        if st.button("✅ Verify Email Setup"):
            if sender_email and sender_password:
                sender = EmailSender(sender_email, sender_password)
                is_valid, msg = sender.validate_email_setup()
                if is_valid:
                    st.success(msg)
                    st.session_state.sender_email = sender_email
                    st.session_state.sender_password = sender_password
                else:
                    st.error(msg)
            else:
                st.warning("⚠️ Please fill in both email and password")
        
        st.markdown("---")
        st.markdown("**📖 How to get App Password:**")
        st.markdown("""
        1. Go to https://myaccount.google.com/security
        2. Find "App passwords" (scroll down)
        3. Select Mail & Windows Computer
        4. Copy the 16-character password
        5. Paste it above (without spaces)
        """)
    
    st.markdown("---")
    
    # Analysis Settings
    st.markdown("### 🔍 Analysis Settings")
    num_companies = st.slider(
        "Companies to find:",
        min_value=3,
        max_value=30,
        value=10,
        step=1
    )
    
    # Job Discovery Mode
    st.markdown("### 🎯 Job Discovery Mode")
    discovery_mode = st.radio(
        "Choose mode:",
        ["Fast (AI-Generated)", "Real Jobs (Scraper)", "Hybrid (Both)"],
        help="""
        • Fast: 30 companies in 10 seconds (AI-generated)
        • Real Jobs: Live postings from LinkedIn, Reddit, GitHub
        • Hybrid: Best of both worlds (AI + Real scraping)
        """
    )
    
    # Show mode info
    if discovery_mode == "Fast (AI-Generated)":
        st.info("⚡ Fast mode uses AI to generate company lists instantly")
    elif discovery_mode == "Real Jobs (Scraper)":
        st.info("🔍 Scraper mode finds actual live job postings (takes longer)")
    else:
        st.info("🎯 Hybrid mode combines AI speed with real job verification")
    
    st.markdown("---")
    
    # Location Preference
    st.markdown("### 🌍 Location Preference")
    location_option = st.radio(
        "Filter by location:",
        ["All Locations", "Specific Region", "Custom"]
    )
    
    if location_option == "Specific Region":
        regions = list(st.session_state.location_matcher.get_regions().keys())
        preferred_location = st.selectbox("Select region:", regions)
    elif location_option == "Custom":
        preferred_location = st.text_input("Enter location:", "")
    else:
        preferred_location = None
    
    include_remote = st.checkbox("Include remote jobs", value=True)
    
    st.markdown("---")
    st.markdown("""
        ### 📚 About JobFinder Pro
        
        **Features:**
        - 🤖 AI CV Analysis
        - 🔍 Real Job Scraping
        - ✉️ Personalized Emails
        - 📎 **CV Attachments**
        - 📊 Application Tracking
        - 📧 Direct Email Sending
        
        **Powered by:** Anthropic Claude API
    """)

# ============================================================
# MAIN CONTENT - UPLOAD SECTION
# ============================================================

st.markdown("### 📤 Step 1: Upload Your CV")
uploaded_file = st.file_uploader(
    "Drag and drop your CV or click to browse",
    type=["pdf", "txt", "docx"],
    help="Supported formats: PDF, TXT, DOCX"
)

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        temp_path = tmp.name
        st.session_state.uploaded_cv_path = temp_path  # Store for email attachment
    
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Run button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        run_button = st.button("🚀 Start Analysis", width="stretch")
    
    if run_button:
        st.session_state.processing = True
        
        # Create placeholders for progress
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Determine mode
            if discovery_mode == "Fast (AI-Generated)":
                mode = "ai"
            elif discovery_mode == "Real Jobs (Scraper)":
                mode = "scraper"
            else:
                mode = "hybrid"
            
            # Show mode being used
            with status_placeholder.container():
                st.info(f"🎯 Using {mode.upper()} Mode...")
            
            time.sleep(1)
            
            # Run complete workflow
            engine = st.session_state.engine
            
            with progress_placeholder.container():
                st.info("🚀 Running complete workflow...")
                progress_bar = st.progress(0)
            
            # Run workflow with selected mode
            results = engine.run_full_pipeline(
                cv_path=temp_path,
                num_companies=num_companies,
                mode=mode,
                location=preferred_location if preferred_location else "",
                include_remote=include_remote
            )
            
            progress_bar.progress(100)
            
            # Store results
            st.session_state.results = results
            
            # Clear progress indicators
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Success message
            st.balloons()
            st.success(f"🎉 Analysis Complete ({mode.upper()} Mode)! See results below.")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        
        finally:
            st.session_state.processing = False

# ============================================================
# RESULTS DISPLAY
# ============================================================

if st.session_state.results:
    results = st.session_state.results
    cv_data = results['cv_analysis']
    companies = results['companies']
    emails = results['emails']
    
    st.divider()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 Candidate", cv_data.get('name', 'Unknown'))
    
    with col2:
        st.metric("📅 Experience", f"{cv_data.get('experience_years', 0)} years")
    
    with col3:
        verified_count = sum(1 for c in companies if c.get('verified'))
        st.metric("🏢 Companies", f"{len(companies)} ({verified_count} verified)")
    
    with col4:
        st.metric("✉️ Emails", len(emails))
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 CV Analysis",
        "🏢 Companies",
        "✉️ Emails",
        "📊 Tracker",
        "📧 Send Emails",
        "📥 Download"
    ])
    
    # ============================================================
    # TAB 1: CV ANALYSIS
    # ============================================================
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Personal Information")
            st.write(f"**Name:** {cv_data.get('name', 'N/A')}")
            st.write(f"**Email:** {cv_data.get('email', 'N/A')}")
            st.write(f"**Phone:** {cv_data.get('phone', 'N/A')}")
        
        with col2:
            st.markdown("### 📊 Experience")
            st.write(f"**Years:** {cv_data.get('experience_years', 0)}")
            st.write(f"**Industries:** {', '.join(cv_data.get('industries', []))}")
        
        st.markdown("### 💼 Job Titles")
        for title in cv_data.get('job_titles', []):
            st.write(f"• {title}")
        
        st.markdown("### 🛠️ Skills")
        skills = cv_data.get('skills', [])
        skills_text = ", ".join(skills[:15])
        if len(skills) > 15:
            skills_text += f", ... and {len(skills) - 15} more"
        st.write(skills_text)
        
        st.markdown("### 📝 Professional Summary")
        st.write(cv_data.get('summary', 'N/A'))
    
    # ============================================================
    # TAB 2: COMPANIES
    # ============================================================
    with tab2:
        verified_count = sum(1 for c in companies if c.get('verified'))
        ai_count = len(companies) - verified_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Companies", len(companies))
        with col2:
            st.metric("✅ Verified Jobs", verified_count)
        with col3:
            st.metric("🤖 AI-Generated", ai_count)
        
        st.markdown(f"### 🏢 {len(companies)} Companies Found")
        
        search_term = st.text_input("🔍 Search companies...", "")
        
        filtered_companies = [
            c for c in companies
            if search_term.lower() in c.get('company_name', '').lower()
        ] if search_term else companies
        
        for i, company in enumerate(filtered_companies, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Show verification badge
                    if company.get('verified'):
                        badge = '<span class="verified-badge">✅ VERIFIED</span>'
                    else:
                        badge = '<span class="ai-badge">🤖 AI</span>'
                    
                    st.markdown(f"**{i}. {company.get('company_name', 'Company')}** {badge}", unsafe_allow_html=True)
                    st.write(f"📌 Industry: {company.get('industry', 'N/A')}")
                    st.write(f"🌐 Website: {company.get('website', 'N/A')}")
                    st.write(f"📧 Email: {company.get('email', 'N/A')}")
                    
                    # Show job-specific info for verified jobs
                    if company.get('verified'):
                        st.write(f"💼 Position: {company.get('job_title', 'N/A')}")
                        st.write(f"📍 Location: {company.get('location', 'N/A')}")
                        st.write(f"🔗 Source: {company.get('source', 'N/A')}")
                        if company.get('job_url'):
                            st.markdown(f"[View Job Posting]({company.get('job_url')})")
                
                with col2:
                    status = company.get('hiring_status', 'Unknown')
                    st.write(f"Status: **{status}**")
            
            st.divider()
    
    # ============================================================
    # TAB 3: EMAILS
    # ============================================================
    with tab3:
        st.markdown(f"### ✉️ {len(emails)} Personalized Emails")
        
        email_selector = st.selectbox(
            "Select email to preview:",
            range(len(emails)),
            format_func=lambda x: f"{x+1}. {emails[x].get('company_name', 'Company')}"
        )
        
        selected_email = emails[email_selector]
        
        st.markdown("#### 📨 Email Preview")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**To:** {selected_email.get('company_email', 'N/A')}")
            st.write(f"**From:** {selected_email.get('candidate_email', 'N/A')}")
        
        st.write(f"**Subject:** {selected_email.get('subject', 'N/A')}")
        st.markdown("---")
        st.write(selected_email.get('body', 'N/A'))
    
    # ============================================================
    # TAB 4: APPLICATION TRACKER
    # ============================================================
    with tab4:
        st.markdown("### 📊 Application Tracker")
        
        tracker = st.session_state.tracker
        stats = tracker.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📧 Total", stats['total_applications'])
        with col2:
            st.metric("✅ Sent", stats['emails_sent'])
        with col3:
            st.metric("💬 Responses", stats['responses_received'])
        with col4:
            st.metric("🎤 Interviews", stats['interviews_scheduled'])
        
        st.markdown("---")
        
        if tracker.get_all_applications():
            st.markdown("#### 📋 All Applications")
            apps_df = pd.DataFrame(tracker.get_all_applications())
            st.dataframe(apps_df, width="stretch")
    
    # ============================================================
    # TAB 5: SEND EMAILS (WITH CV ATTACHMENT)
    # ============================================================
    with tab5:
        st.markdown("### 📧 Send Emails with CV Attachment")
        
        if st.session_state.sender_email and st.session_state.sender_password:
            st.success("✅ Email configured")
            
            # CV Attachment Option
            st.markdown("#### 📎 Attachment Options")
            attach_cv = st.checkbox("📎 Attach CV to all emails", value=True)
            
            if attach_cv and st.session_state.uploaded_cv_path:
                cv_filename = Path(st.session_state.uploaded_cv_path).name
                st.info(f"✅ CV will be attached: {cv_filename}")
            elif attach_cv:
                st.warning("⚠️ No CV file available. Please upload a CV first.")
            
            st.markdown("---")
            
            send_mode = st.radio("Select sending mode:", ["Preview", "Send All", "Send Selected"])
            
            if send_mode == "Send All":
                if st.button("🚀 Send All Emails", width="stretch"):
                    sender = EmailSender(st.session_state.sender_email, st.session_state.sender_password)
                    
                    emails_to_send = [
                        {
                            "to": email.get('company_email'),
                            "subject": email.get('subject'),
                            "body": email.get('body')
                        }
                        for email in emails
                    ]
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📧 Sending emails...")
                    
                    # Send with CV attachment if enabled
                    results = sender.send_batch_emails(
                        emails_to_send,
                        cv_path=st.session_state.uploaded_cv_path if attach_cv else None
                    )
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    # Track in application tracker
                    for i, email in enumerate(emails):
                        tracker.add_application(
                            candidate_name=cv_data.get('name'),
                            company_name=email.get('company_name'),
                            company_email=email.get('company_email'),
                            email_sent=True
                        )
                    
                    st.success(f"✅ {results['sent']} emails sent successfully!")
                    if results['failed'] > 0:
                        st.warning(f"⚠️ {results['failed']} emails failed")
                    
                    # Show details
                    with st.expander("📊 View Details"):
                        for detail in results['details']:
                            status_icon = "✅" if detail['status'] == 'sent' else "❌"
                            st.write(f"{status_icon} {detail['to']} - {detail['timestamp']}")
            
            elif send_mode == "Send Selected":
                selected_emails = st.multiselect(
                    "Select emails to send:",
                    range(len(emails)),
                    format_func=lambda x: emails[x].get('company_name')
                )
                
                if st.button("📧 Send Selected", width="stretch"):
                    if not selected_emails:
                        st.warning("⚠️ Please select at least one email")
                    else:
                        sender = EmailSender(st.session_state.sender_email, st.session_state.sender_password)
                        
                        emails_to_send = [
                            {
                                "to": emails[i].get('company_email'),
                                "subject": emails[i].get('subject'),
                                "body": emails[i].get('body')
                            }
                            for i in selected_emails
                        ]
                        
                        # Send with CV attachment
                        results = sender.send_batch_emails(
                            emails_to_send,
                            cv_path=st.session_state.uploaded_cv_path if attach_cv else None
                        )
                        
                        for i in selected_emails:
                            tracker.add_application(
                                candidate_name=cv_data.get('name'),
                                company_name=emails[i].get('company_name'),
                                company_email=emails[i].get('company_email'),
                                email_sent=True
                            )
                        
                        st.success(f"✅ {results['sent']} emails sent!")
                        if results['failed'] > 0:
                            st.warning(f"⚠️ {results['failed']} emails failed")
        else:
            st.warning("⚠️ Please configure email in Settings first")
    
    # ============================================================
    # TAB 6: DOWNLOAD (FIXED CSV EXPORT)
    # ============================================================
    with tab6:
        st.markdown("### 📥 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cv_json = json.dumps(cv_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📋 CV Analysis (JSON)",
                data=cv_json,
                file_name="cv_analysis.json",
                mime="application/json"
            )
        
        with col2:
            companies_json = json.dumps(companies, indent=2, ensure_ascii=False)
            st.download_button(
                label="🏢 Companies (JSON)",
                data=companies_json,
                file_name="companies_output.json",
                mime="application/json"
            )
        
        with col3:
            emails_json = json.dumps(emails, indent=2, ensure_ascii=False)
            st.download_button(
                label="✉️ Emails (JSON)",
                data=emails_json,
                file_name="emails_output.json",
                mime="application/json"
            )
        
        st.divider()
        
        # Export as CSV (FIXED - handles all fields dynamically)
        st.markdown("### 📊 Export as CSV")
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame(companies)
        csv_data = df.to_csv(index=False)
        
        st.download_button(
            label="🏢 Companies as CSV",
            data=csv_data,
            file_name="companies_output.csv",
            mime="text/csv"
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666;'>
        <p>🚀 <b>JobFinder Pro v2.0</b> | AI + Real Jobs + CV Attachments</p>
        <p>Powered by Anthropic Claude API | Made with ❤️ for job seekers</p>
    </div>
    """, unsafe_allow_html=True)