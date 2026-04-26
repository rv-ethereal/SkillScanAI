# SkillScan AI

SkillScan AI is an agent that analyzes a candidate's resume against a job description, evaluates their skills, conducts an AI interview on missing skills, and generates a personalized learning roadmap.

## Setup Instructions

1. Clone or download this project.
2. Navigate into the project folder:
   ```bash
   cd SkillScanAI
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your OpenAI API Key (see `.env.example`):
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## How to use
- Paste your Job Description.
- Upload a candidate's resume (PDF or Text).
- Click **Analyze Skills**.
- View the match score and extracted/missing skills.
- The AI will then conduct a short quiz to evaluate adjacent or missing skills.
- Enter your response and receive a score and feedback.
- A personalized learning plan will be generated based on the missing skills.
