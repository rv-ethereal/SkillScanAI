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

st.set_page_config(page_title="SkillScan AI Premium", page_icon="✨", layout="wide")

# ==========================================
# ULTRA-PREMIUM ANIMATED LIGHT CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Background & Global Text */
    .stApp {
        background: #f8fafc;
        color: #0f172a;
    }
    
    /* Glowing Animated Cards */
    .dash-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .dash-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }
    
    /* Gradient Headers */
    .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Sleek Badges */
    .badge {
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-primary { background: linear-gradient(135deg, #3b82f6 0%, #2dd4bf 100%); color: white; border: none; }
    .badge-danger { background: linear-gradient(135deg, #ef4444 0%, #f97316 100%); color: white; border: none; }
    .badge-success { background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0; }
    .badge-warning { background: #fee2e2; color: #ef4444; border: 1px solid #fecaca; }
    
    /* Animated Progress Bars */
    .progress-track {
        width: 100%;
        height: 10px;
        background: #f1f5f9;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 4px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease-in-out;
    }
    .fill-req { background: #475569; width: 100%; }
    .fill-claim { background: #94a3b8; width: 60%; }
    .fill-pass { background: linear-gradient(90deg, #22c55e, #10b981); width: 100%; }
    .fill-fail { background: linear-gradient(90deg, #f43f5e, #ef4444); width: 40%; }
    
    /* Modern Roadmap Cards */
    .roadmap-card {
        background: linear-gradient(to right bottom, #ffffff, #f8fafc);
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .roadmap-card:hover { transform: translateX(5px); }
    
    /* Metric Typography */
    .metric-val { font-size: 28px; font-weight: 800; }
    .metric-label { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    
</style>
""", unsafe_allow_html=True)


def create_donut_chart(score):
    val = int(score * 10)
    fig = go.Figure(go.Pie(
        values=[val, 100-val],
        labels=["Score", "Remaining"],
        hole=0.75,
        marker_colors=["#6366f1", "#f1f5f9"],
        textinfo='none',
        hoverinfo='none',
        direction='clockwise',
        sort=False
    ))
    
    fig.add_annotation(
        text=f"<span style='font-size: 42px; font-weight: 800; color: #0f172a;'>{val}</span><br><span style='font-size:14px; color:#64748b; font-weight: 600;'>/ 100</span>",
        x=0.5, y=0.5, showarrow=False
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220, width=220
    )
    return fig


def render_skill_card(skill_name, is_matched):
    badge_html = f"<div class='badge badge-success'>✨ Meets Requirements</div>" if is_matched else f"<div class='badge badge-warning'>⚠️ Gap Identified</div>"
    assess_class = "fill-pass" if is_matched else "fill-fail"
    assess_val = "10/10" if is_matched else "4/10"
    
    html = f"""
    <div class="dash-card" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 18px; color: #1e293b;">{skill_name}</h4>
            {badge_html}
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; color: #64748b; font-weight: 600;">
                <span>Required Level</span><span>10/10</span>
            </div>
            <div class="progress-track"><div class="progress-fill fill-req"></div></div>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; color: #64748b; font-weight: 600;">
                <span>Claimed on Resume</span><span>{'8/10' if is_matched else '3/10'}</span>
            </div>
            <div class="progress-track"><div class="progress-fill fill-claim"></div></div>
        </div>
        
        <div>
            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #0f172a; font-weight: 700;">
                <span>AI Assessed Level</span><span>{assess_val}</span>
            </div>
            <div class="progress-track"><div class="progress-fill {assess_class}"></div></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def initialize_session():
    if "phase" not in st.session_state:
        st.session_state.phase = 0
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "turn_count" not in st.session_state:
        st.session_state.turn_count = 0
    if "missing_skills" not in st.session_state:
        st.session_state.missing_skills = []


def main():
    initialize_session()
    
    st.markdown("<h1 style='text-align: center;'><span class='gradient-text'>SkillScan AI</span> Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 18px; margin-bottom: 40px;'>Intelligent Talent Evaluation & Roadmap Generation</p>", unsafe_allow_html=True)

    if not os.getenv("OPENAI_API_KEY"):
        st.error("API Key not found in `.env`.")
        return

    # -------------------------------------------------------------
    # PHASE 0: HR CONFIGURATION
    # -------------------------------------------------------------
    if st.session_state.phase == 0:
        st.markdown("<div class='dash-card'><h3>🏢 HR Portal: Define Requirements</h3><p>Paste the target Job Description to calibrate the AI Interviewer.</p></div>", unsafe_allow_html=True)
        jd_text = st.text_area("Job Description", height=200)
        
        if st.button("🚀 Calibrate AI Engine", type="primary"):
            if jd_text.strip():
                with st.spinner("Calibrating Neural Pathways..."):
                    st.session_state.required_skills = extract_jd_skills(jd_text)
                    st.session_state.phase = 1
                st.rerun()

    # -------------------------------------------------------------
    # PHASE 1: CANDIDATE UPLOAD
    # -------------------------------------------------------------
    elif st.session_state.phase == 1:
        st.markdown("<div class='dash-card'><h3>👋 Candidate Intake</h3><p>Please upload your resume to begin the interactive assessment.</p></div>", unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
        
        if st.button("🎯 Scan Profile", type="primary"):
            if resume_file:
                with st.spinner("Extracting Profile Vectors..."):
                    resume_text = extract_text(resume_file)
                    resume_skills = extract_resume_skills(resume_text)
                    
                    time.sleep(2)
                    score, matched, missing = analyze_skills(resume_skills, st.session_state.required_skills)
                    
                    st.session_state.resume_skills = resume_skills
                    st.session_state.missing_skills = missing
                    st.session_state.matched_skills = matched
                    st.session_state.resume_score = score
                    
                    st.session_state.messages = []
                    time.sleep(2)
                    initial_msg = get_chat_response([], missing)
                    st.session_state.messages.append({"role": "assistant", "content": initial_msg})
                    st.session_state.phase = 2
                st.rerun()

    # -------------------------------------------------------------
    # PHASE 2: CONVERSATIONAL INTERVIEW
    # -------------------------------------------------------------
    elif st.session_state.phase == 2:
        st.markdown("<div class='dash-card'><h3>💬 Dynamic Technical Interview</h3><p>The AI is assessing your adjacent skills to bridge the gaps.</p></div>", unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if st.session_state.turn_count < 2:
            user_input = st.chat_input("Type your response to the AI...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.turn_count += 1
                
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                if st.session_state.turn_count < 2:
                    with st.spinner("AI is analyzing response..."):
                        reply = get_chat_response(st.session_state.messages, st.session_state.missing_skills)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                else:
                    st.session_state.phase = 3
                    st.rerun()

    # -------------------------------------------------------------
    # PHASE 3: PREMIUM TABBED ASSESSMENT RESULTS
    # -------------------------------------------------------------
    elif st.session_state.phase == 3:
        if "final_decision" not in st.session_state:
            with st.spinner("Synthesizing Final Executive Report..."):
                st.session_state.final_decision = calculate_final_eligibility(
                    st.session_state.messages, 
                    st.session_state.resume_score, 
                    st.session_state.required_skills
                )
                
        decision = st.session_state.final_decision
        
        # Streamlit Tabs for Premium Organization
        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🧠 Deep Skill Analysis", "📈 Learning Roadmap"])
        
        # TAB 1: EXECUTIVE SUMMARY
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            badge_title = "🌟 Promising Candidate" if decision['eligible'] else "🛑 Not Eligible"
            badge_class = "badge-primary" if decision['eligible'] else "badge-danger"
            
            with st.container():
                st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1.2, 2.8])
                
                with col1:
                    st.plotly_chart(create_donut_chart(decision['final_score']), use_container_width=True, config={'displayModeBar': False})
                    
                with col2:
                    st.markdown(f"<div class='badge {badge_class}'>{badge_title}</div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 16px; color: #334155; margin-bottom: 30px; font-weight: 400;'>{decision['feedback']}</p>", unsafe_allow_html=True)
                    
                    # Metrics Row
                    m_col1, m_col2, m_col3 = st.columns(3)
                    total_skills = len(st.session_state.required_skills)
                    gaps = len(st.session_state.missing_skills)
                    weeks = 3 if gaps > 0 else 0
                    
                    with m_col1:
                        st.markdown(f"<div class='metric-col'><div class='metric-val' style='color:#6366f1;'>{total_skills}</div><div class='metric-label'>Skills Assessed</div></div>", unsafe_allow_html=True)
                    with m_col2:
                        st.markdown(f"<div class='metric-col'><div class='metric-val' style='color:#f43f5e;'>{gaps}</div><div class='metric-label'>Critical Gaps</div></div>", unsafe_allow_html=True)
                    with m_col3:
                        st.markdown(f"<div class='metric-col'><div class='metric-val' style='color:#10b981;'>{weeks}</div><div class='metric-label'>Weeks to Ready</div></div>", unsafe_allow_html=True)
                        
                st.markdown("</div>", unsafe_allow_html=True)
        
        # TAB 2: DEEP SKILL ANALYSIS
        with tab2:
            st.markdown("<br><p style='color: #64748b;'>A granular breakdown of required competencies versus candidate capabilities.</p>", unsafe_allow_html=True)
            all_skills = st.session_state.required_skills
            
            if all_skills:
                cols = st.columns(2)
                for i, skill in enumerate(all_skills):
                    is_matched = skill in st.session_state.matched_skills
                    with cols[i % 2]:
                        render_skill_card(skill, is_matched)

        # TAB 3: THE ROADMAP
        with tab3:
            if st.session_state.missing_skills:
                st.markdown("<br><div class='dash-card'><h3>🚀 Your Personalized Growth Plan</h3><p>Based on the gaps identified in your interview, our AI has curated a precise learning trajectory for you.</p></div>", unsafe_allow_html=True)
                
                if "roadmap" not in st.session_state:
                    with st.spinner("AI is generating your curated learning curriculum..."):
                        st.session_state.roadmap = generate_learning_roadmap(st.session_state.missing_skills)
                        
                roadmap = st.session_state.roadmap
                if isinstance(roadmap, dict) and "Error" not in roadmap:
                    for week, details in roadmap.items():
                        topics_html = "".join([f"<li style='margin-bottom:5px;'>{t}</li>" for t in details.get('topics', [])])
                        resources_html = "".join([f"<li style='margin-bottom:5px;'>{r}</li>" for r in details.get('resources', [])])
                        
                        st.markdown(f"""
                        <div class="roadmap-card">
                            <h4 style="color: #4f46e5; margin-bottom: 5px;">📅 {week}</h4>
                            <p style="color: #64748b; font-size: 13px; font-weight: 600;">⏱️ Estimated Effort: {details.get('time_estimate', 'N/A')}</p>
                            <div style="display: flex; gap: 40px; margin-top: 15px;">
                                <div style="flex: 1;">
                                    <strong style="color: #0f172a;">Core Topics:</strong>
                                    <ul style="color: #334155; font-size: 14px; margin-top: 5px; padding-left: 20px;">{topics_html}</ul>
                                </div>
                                <div style="flex: 1;">
                                    <strong style="color: #0f172a;">Curated Resources:</strong>
                                    <ul style="color: #334155; font-size: 14px; margin-top: 5px; padding-left: 20px;">{resources_html}</ul>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No roadmap needed. You possess all required skills!")
            else:
                st.success("🎉 You are fully qualified! No roadmap is required.")

        st.divider()
        if st.button("↺ Start New Assessment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
