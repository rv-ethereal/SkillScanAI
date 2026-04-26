import streamlit as st
import os
import time
import plotly.graph_objects as go
from dotenv import load_dotenv

from src.parser import extract_text
from src.extractor import extract_resume_skills, extract_jd_skills
from src.analyzer import analyze_skills
from src.interviewer import get_chat_response, calculate_final_eligibility
from src.planner import generate_learning_roadmap

load_dotenv()

st.set_page_config(page_title="SkillScan AI Agent", page_icon="🤖", layout="wide")

# Custom Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark Premium Theme Overrides */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    /* Status Badges */
    .badge-pass {
        background: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .badge-fail {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Match Score", 'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [None, 10], 'tickcolor': "white"},
            'bar': {'color': "#818cf8"},
            'steps': [
                {'range': [0, 4], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [4, 7], 'color': "rgba(234, 179, 8, 0.3)"},
                {'range': [7, 10], 'color': "rgba(34, 197, 94, 0.3)"}
            ],
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=300
    )
    return fig

def initialize_session():
    if "phase" not in st.session_state:
        st.session_state.phase = 0  # 0: HR, 1: Upload, 2: Interview, 3: Verdict
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "turn_count" not in st.session_state:
        st.session_state.turn_count = 0
    if "missing_skills" not in st.session_state:
        st.session_state.missing_skills = []

def main():
    initialize_session()
    
    st.markdown("<h1 style='text-align: center;'><span class='gradient-text'>SkillScan AI</span> Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Conversational Assessment & Eligibility Engine</p>", unsafe_allow_html=True)
    st.divider()

    if not os.getenv("OPENAI_API_KEY"):
        st.error("API Key not found in `.env`. Please add OPENAI_API_KEY.")
        return

    # -------------------------------------------------------------
    # PHASE 0: HR CONFIGURATION
    # -------------------------------------------------------------
    if st.session_state.phase == 0:
        st.markdown("<div class='glass-card'><h3>👨‍💼 HR Portal: Configure Agent</h3></div>", unsafe_allow_html=True)
        jd_text = st.text_area("Job Description", height=250, placeholder="Paste the full job description here...")
        
        if st.button("Initialize Agent", type="primary"):
            if jd_text.strip():
                with st.spinner("Agent parsing requirements..."):
                    st.session_state.required_skills = extract_jd_skills(jd_text)
                    st.session_state.phase = 1
                st.rerun()
            else:
                st.warning("Please provide a Job Description.")

    # -------------------------------------------------------------
    # PHASE 1: CANDIDATE UPLOAD & INITIAL ANALYSIS
    # -------------------------------------------------------------
    elif st.session_state.phase == 1:
        st.markdown("<div class='glass-card'><h3>👋 Candidate Portal: Welcome</h3><p>I am your AI Assessor. Please upload your resume so we can begin.</p></div>", unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
        
        if st.button("Analyze Profile", type="primary"):
            if resume_file:
                with st.spinner("Extracting & Analyzing..."):
                    resume_text = extract_text(resume_file)
                    resume_skills = extract_resume_skills(resume_text)
                    
                    time.sleep(2) # Smart delay to prevent Free Tier rate limit crash
                    score, matched, missing = analyze_skills(resume_skills, st.session_state.required_skills)
                    
                    st.session_state.resume_skills = resume_skills
                    st.session_state.missing_skills = missing
                    st.session_state.matched_skills = matched
                    st.session_state.resume_score = score
                    
                    # Generate the very first question to kick off chat
                    st.session_state.messages = []
                    time.sleep(2) # Smart delay
                    initial_msg = get_chat_response([], missing)
                    st.session_state.messages.append({"role": "assistant", "content": initial_msg})
                    
                    st.session_state.phase = 2
                st.rerun()
            else:
                st.warning("Please upload a resume.")

    # -------------------------------------------------------------
    # PHASE 2: CONVERSATIONAL INTERVIEW
    # -------------------------------------------------------------
    elif st.session_state.phase == 2:
        col1, col2 = st.columns([1, 2])
        
        # Left Column: Analytics Visuals
        with col1:
            st.markdown("<div class='glass-card'><h4>Initial Resume Match</h4>", unsafe_allow_html=True)
            st.plotly_chart(create_gauge_chart(st.session_state.resume_score), use_container_width=True)
            
            with st.expander("Matched Skills ✅"):
                st.write(", ".join(st.session_state.matched_skills) if st.session_state.matched_skills else "None")
            with st.expander("Missing Skills ❌"):
                st.write(", ".join(st.session_state.missing_skills) if st.session_state.missing_skills else "None")
            st.markdown("</div>", unsafe_allow_html=True)

        # Right Column: Chat Interface
        with col2:
            st.markdown("<div class='glass-card'><h4>AI Technical Interview</h4>", unsafe_allow_html=True)
            
            # Display chat messages
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # Max 2 turns (User replies 2 times)
            if st.session_state.turn_count < 2:
                user_input = st.chat_input("Type your answer here...")
                if user_input:
                    # Append user message
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.turn_count += 1
                    
                    with st.chat_message("user"):
                        st.markdown(user_input)
                    
                    # If under max turns, ask next question
                    if st.session_state.turn_count < 2:
                        with st.spinner("AI is typing..."):
                            reply = get_chat_response(st.session_state.messages, st.session_state.missing_skills)
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            st.rerun()
                    else:
                        # End of interview
                        st.session_state.phase = 3
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # PHASE 3: FINAL VERDICT & ROADMAP
    # -------------------------------------------------------------
    elif st.session_state.phase == 3:
        st.markdown("<h2 style='text-align: center;'>Final Assessment Verdict</h2>", unsafe_allow_html=True)
        
        if "final_decision" not in st.session_state:
            with st.spinner("AI is synthesizing results and making a final decision..."):
                st.session_state.final_decision = calculate_final_eligibility(
                    st.session_state.messages, 
                    st.session_state.resume_score, 
                    st.session_state.required_skills
                )
                
        decision = st.session_state.final_decision
        
        # Display Verdict Card
        card_html = f"""
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <h1 style="font-size: 3rem; margin-bottom: 10px;">
                <span class="{'badge-pass' if decision['eligible'] else 'badge-fail'}">
                    {'🌟 ELIGIBLE' if decision['eligible'] else '❌ NOT ELIGIBLE'}
                </span>
            </h1>
            <h3>Final Score: {decision['final_score']} / 10.0</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; max-width: 600px; margin: 20px auto;">{decision['feedback']}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Roadmap Section (Only show if not perfect score or not eligible)
        if not decision['eligible'] or st.session_state.missing_skills:
            st.divider()
            st.markdown("<h3>Your Personalized Learning Roadmap</h3>", unsafe_allow_html=True)
            st.caption("Based on the gaps identified in your resume and interview, follow this 3-week plan to upskill.")
            
            if "roadmap" not in st.session_state:
                with st.spinner("Generating curated learning plan..."):
                    st.session_state.roadmap = generate_learning_roadmap(st.session_state.missing_skills)
                    
            roadmap = st.session_state.roadmap
            if isinstance(roadmap, dict) and "Error" not in roadmap:
                cols = st.columns(3)
                for idx, (week, details) in enumerate(roadmap.items()):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="glass-card" style="height: 100%;">
                            <h4 class="gradient-text">{week}</h4>
                            <p>⏱️ <b>{details.get('time_estimate', 'N/A')}</b></p>
                            <hr style="border-color: rgba(255,255,255,0.1)">
                            <b>Topics:</b>
                            <ul>{''.join([f'<li>{t}</li>' for t in details.get('topics', [])])}</ul>
                            <b>Resources:</b>
                            <ul>{''.join([f'<li>{r}</li>' for r in details.get('resources', [])])}</ul>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.write(roadmap)

        if st.button("Start Over (HR Portal)"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
