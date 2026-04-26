<div align="center">
  <h1>✨ SkillScan AI</h1>
  <p><strong>Intelligent Talent Evaluation & Autonomous Interview Agent</strong></p>
</div>

## 📌 Overview
SkillScan AI transforms the standard static resume screening process into a dynamic, conversational assessment. It is an agentic application designed to evaluate a candidate's resume against a specific Job Description (JD), calculate overlaps, and autonomously conduct a technical interview to assess any missing skills before delivering a final hiring verdict and personalized learning roadmap.

---

## 🚀 Core Features
1. **Multi-Persona Workflow**: Features an HR Persona for configuring job requirements and a Candidate Persona for interactive evaluations.
2. **Deterministic Extraction & Scoring**: Uses advanced LLM JSON-schema forcing and Python mathematics to extract skills from PDFs and calculate precise string-matching scores.
3. **Agentic Conversational Interview**: The AI identifies missing skills and acts as a strict technical interviewer, remembering multi-turn chat history to probe the candidate's adjacent knowledge.
4. **Premium Tabbed Dashboard**: 
   - **Executive Summary**: Renders dynamic Plotly Donut Charts and eligibility badges.
   - **Deep Skill Analysis**: Visualizes required vs. claimed vs. assessed skill levels using custom-built CSS animated progress bars.
   - **Learning Roadmap**: Generates a bespoke 3-week actionable learning plan for candidates who don't perfectly meet the JD.

---

## 🛠️ Technology Stack
- **Frontend**: [Streamlit](https://streamlit.io/) with heavily customized raw HTML/CSS injections for a premium light-mode dashboard and glassmorphism elements.
- **Backend**: Python 3.x
- **LLM Engine**: [Groq API](https://groq.com/) utilizing **LLaMA-3.1-8B-Instant** via OpenAI-compatible endpoints for lightning-fast inference and rate-limit bypassing.
- **Data Visualization**: [Plotly](https://plotly.com/python/)
- **Document Parsing**: `PyPDF2`

---

## 💻 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rv-ethereal/SkillScanAI.git
cd SkillScanAI
```

### 2. Install Dependencies
Make sure you have Python installed. Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your Groq API Key:
```env
OPENAI_API_KEY="gsk_your_groq_api_key_here"
```
*(Note: Although the variable is named `OPENAI_API_KEY`, the application routes to the Groq API endpoint for faster performance).*

### 4. Run the Application
Start the Streamlit development server:
```bash
python -m streamlit run app.py
```

---

## 🌐 Live Deployment
The project is continuously deployed and hosted on Streamlit Community Cloud.
**[Access the Live Application Here](https://skillscanai.streamlit.app/)**
