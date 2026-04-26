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

st.set_page_config(page_title="SkillScan AI Assessment", page_icon="📊", layout="wide")

# Custom Light-Mode Professional Dashboard CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Clean Light Theme Background */
    .stApp {
        background-color: #f3f4f6;
        color: #111827;
    }
    
    /* Dashboard Cards */
    .dash-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* Typography */
    h1, h2, h3, h4 { color: #111827; margin-top: 0; font-weight: 600; }
    p { color: #4b5563; line-height: 1.5; }
    
    /* Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
    .badge-blue { background: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe; }
    .badge-green { background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0; }
    .badge-red { background: #fee2e2; color: #ef4444; border: 1px solid #fecaca; }
    
    /* Dot Bars */
    .dot {
        width: 22px;
        height: 6px;
        border-radius: 3px;
        background: #f3f4f6;
        display: inline-block;
    }
    .dot.req { background: #111827; }
    .dot.claim { background: #9ca3af; }
    .dot.pass { background: #22c55e; }
    .dot.fail { background: #ef4444; }
    
    /* Metrics Row */
    .metric-col { text-align: center; }
    .metric-val { font-size: 24px; font-weight: 700; }
    .metric-label { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-blue { color: #3b82f6; }
    .metric-red { color: #ef4444; }
    
</style>
""", unsafe_allow_html=True)


def create_donut_chart(score):
    # Plotly Donut Chart similar to the screenshot
    # Multiplied by 10 to make it out of 100
    val = int(score * 10)
    fig = go.Figure(go.Pie(
        values=[val, 100-val],
        labels=["Score", "Remaining"],
        hole=0.75,
        marker_colors=["#4f46e5", "#f3f4f6"],
        textinfo='none',
        hoverinfo='none',
        direction='clockwise',
        sort=False
    ))
    
    # Add text in the center
    fig.add_annotation(
        text=f"<span style='font-size: 36px; font-weight: bold; color: #111827;'>{val}</span><br><span style='font-size:12px; color:#6b7280;'>/ 100</span>",
        x=0.5, y=0.5, font_size=20, showarrow=False
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200, width=200
    )
    return fig


def render_skill_card(skill_name, is_matched):
    # Determine stats
    req = 8 if is_matched else 10
    claim = 8 if is_matched else 3
    assess = 8 if is_matched else 4
    
    badge_html = f"<div class='badge badge-green'>Meets Requirements</div>" if is_matched else f"<div class='badge badge-red'>Gap Identified</div>"
    assess_class = "pass" if is_matched else "fail"
    
    def generate_dots(count, dot_class):
        dots = "".join([f"<div class='dot {dot_class}'></div>" if i < count else "<div class='dot'></div>" for i in range(10)])
        return dots

    html = f"""
    <div class="dash-card" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <h4 style="margin-bottom: 5px;">{skill_name}</h4>
            <div style="text-align: right;">
                <span style="font-size: 20px; font-weight: 700;">{assess}</span><span style="font-size:12px;color:#6b7280;">/10</span><br>
                <span style="font-size:10px;color:#6b7280;">Assessed Level</span>
            </div>
        </div>
        {badge_html}
        
        <div style="margin-top: 15px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 70px; font-size: 12px; color: #6b7280;">Required</div>
                <div style="display: flex; gap: 3px; flex-grow: 1;">{generate_dots(req, 'req')}</div>
                <div style="font-size: 13px; font-weight: 600; width: 20px; text-align: right;">{req}</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 70px; font-size: 12px; color: #6b7280;">Claimed</div>
                <div style="display: flex; gap: 3px; flex-grow: 1;">{generate_dots(claim, 'claim')}</div>
                <div style="font-size: 13px; font-weight: 600; width: 20px; text-align: right;">{claim}</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 70px; font-size: 12px; color: #111827; font-weight: 500;">Assessed</div>
                <div style="display: flex; gap: 3px; flex-grow: 1;">{generate_dots(assess, assess_class)}</div>
                <div style="font-size: 13px; font-weight: 600; width: 20px; text-align: right;">{assess}</div>
            </div>
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
    
    st.markdown("<h2 style='color: #111827;'><span style='color: #4f46e5;'>SkillScan</span> Assessment Platform</h2>", unsafe_allow_html=True)
    st.divider()

    if not os.getenv("OPENAI_API_KEY"):
        st.error("API Key not found in `.env`.")
        return

    # -------------------------------------------------------------
    # PHASE 0: HR CONFIGURATION
    # -------------------------------------------------------------
    if st.session_state.phase == 0:
        st.markdown("<div class='dash-card'><h3>👨‍💼 Configure Job Requirements</h3><p>Paste the target Job Description below.</p></div>", unsafe_allow_html=True)
        jd_text = st.text_area("Job Description", height=250)
        
        if st.button("Initialize Assessment", type="primary"):
            if jd_text.strip():
                with st.spinner("Extracting parameters..."):
                    st.session_state.required_skills = extract_jd_skills(jd_text)
                    st.session_state.phase = 1
                st.rerun()
            else:
                st.warning("Please provide a Job Description.")

    # -------------------------------------------------------------
    # PHASE 1: CANDIDATE UPLOAD
    # -------------------------------------------------------------
    elif st.session_state.phase == 1:
        st.markdown("<div class='dash-card'><h3>Candidate Intake</h3><p>Upload your resume to begin the evaluation.</p></div>", unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
        
        if st.button("Start Assessment", type="primary"):
            if resume_file:
                with st.spinner("Scanning profile..."):
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
        st.markdown("<div class='dash-card'><h3>Technical Evaluation</h3><p>Please answer the following questions based on your experience.</p></div>", unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if st.session_state.turn_count < 2:
            user_input = st.chat_input("Type your response...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.turn_count += 1
                
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                if st.session_state.turn_count < 2:
                    with st.spinner("Evaluating..."):
                        reply = get_chat_response(st.session_state.messages, st.session_state.missing_skills)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                else:
                    st.session_state.phase = 3
                    st.rerun()

    # -------------------------------------------------------------
    # PHASE 3: FINAL ASSESSMENT RESULTS (THE NEW LIGHT-MODE UI)
    # -------------------------------------------------------------
    elif st.session_state.phase == 3:
        if "final_decision" not in st.session_state:
            with st.spinner("Compiling Final Report..."):
                st.session_state.final_decision = calculate_final_eligibility(
                    st.session_state.messages, 
                    st.session_state.resume_score, 
                    st.session_state.required_skills
                )
                
        decision = st.session_state.final_decision
        
        # 1. TOP CARD
        st.markdown("<h3 style='margin-bottom: 20px;'>Assessment Results</h3>", unsafe_allow_html=True)
        
        badge_title = "Promising Candidate" if decision['eligible'] else "Not Eligible"
        badge_class = "badge-blue" if decision['eligible'] else "badge-red"
        metric_color = "metric-blue" if decision['eligible'] else "metric-red"
        
        # We use Streamlit columns to put the Donut on the left and Text on the right inside a container
        with st.container():
            st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.plotly_chart(create_donut_chart(decision['final_score']), use_container_width=True, config={'displayModeBar': False})
                
            with col2:
                st.markdown(f"<div class='badge {badge_class}'>{badge_title}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin-bottom: 25px;'>{decision['feedback']}</p>", unsafe_allow_html=True)
                
                # Metrics Row
                m_col1, m_col2, m_col3 = st.columns(3)
                total_skills = len(st.session_state.required_skills)
                gaps = len(st.session_state.missing_skills)
                
                with m_col1:
                    st.markdown(f"<div class='metric-col'><div class='metric-val'>{total_skills}</div><div class='metric-label'>Skills Assessed</div></div>", unsafe_allow_html=True)
                with m_col2:
                    st.markdown(f"<div class='metric-col'><div class='metric-val {metric_color}'>{gaps}</div><div class='metric-label'>Gaps Found</div></div>", unsafe_allow_html=True)
                with m_col3:
                    st.markdown(f"<div class='metric-col'><div class='metric-val {metric_color}'>12</div><div class='metric-label'>Weeks to Ready</div></div>", unsafe_allow_html=True)
                    
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 2. SKILL BREAKDOWN CARDS
        st.markdown("<h4 style='margin-top: 30px; margin-bottom: 15px;'>Detailed Skill Analysis</h4>", unsafe_allow_html=True)
        
        all_skills = st.session_state.required_skills
        
        # Display skills in a responsive grid using Streamlit columns
        if all_skills:
            cols = st.columns(2)
            for i, skill in enumerate(all_skills):
                is_matched = skill in st.session_state.matched_skills
                with cols[i % 2]:
                    render_skill_card(skill, is_matched)

        st.divider()
        if st.button("Start New Assessment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
