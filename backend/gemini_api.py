import os
from dotenv import load_dotenv
import PyPDF2
import re
import google.generativeai as genai

# =========================
# 🔧 SETUP
# =========================
load_dotenv()

# 🔥 API KEY CHECK
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ GEMINI_API_KEY not found in .env")


def _get_model():
    preferred = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    candidates = [preferred, "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    for name in candidates:
        try:
            model = genai.GenerativeModel(name)
            model.generate_content("ping")
            return model
        except Exception:
            continue
    try:
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", []) or []
            if "generateContent" in methods and getattr(m, "name", ""):
                return genai.GenerativeModel(m.name.replace("models/", ""))
    except Exception:
        pass
    raise RuntimeError("No compatible Gemini model found for generateContent.")

# =========================
# 📄 PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(pdf_path):
    resume_text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    resume_text += text + "\n"
    except Exception as e:
        print("❌ PDF Error:", e)

    if not resume_text.strip():
        return "Resume content unavailable (Could not parse PDF)."
    return resume_text.strip()


# =========================
# 🔍 KEYWORD EXTRACTION
# =========================
def extract_resume_keywords(resume_text):
    """
    Intelligently extracts core technologies and key achievements from resume text.
    Used to build context for more personalized questions.
    """
    if "unavailable" in resume_text.lower():
        return {'technologies': [], 'achievements': []}

    tech_stacks = {
        'Languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php'],
        'Frontend': ['react', 'angular', 'vue', 'nextjs', 'tailwind', 'bootstrap', 'flutter', 'redux'],
        'Backend': ['nodejs', 'express', 'django', 'flask', 'spring boot', 'laravel', 'fastapi'],
        'Database': ['postgresql', 'mongodb', 'mysql', 'redis', 'sqlite', 'oracle', 'firebase'],
        'DevOps/Cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
        'Data/AI': ['tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'nlp']
    }

    found_tech = []
    resume_lower = resume_text.lower()

    for category, techs in tech_stacks.items():
        for tech in techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', resume_lower):
                found_tech.append(tech.title())

    achievements = re.findall(r'(\d+(?:%|\+|\s*(?:years?|projects?|users?|months?|clients?|revenue|stars?)))', resume_lower)
    
    return {
        'technologies': list(set(found_tech)),
        'achievements': list(set(achievements))[:6]
    }


# =========================
# 🎯 QUESTION GENERATION (RAG + GEMINI)
# =========================
def generate_questions(resume_text, position, num_questions, seniority_level="fresher"):
    """
    Generate deeply personalized interview questions based on the candidate's actual resume.
    """
    keywords = extract_resume_keywords(resume_text)
    
    difficulty_map = {
        "fresher": "entry-level, focusing on learning agility and core fundamentals",
        "junior": "early-career, testing practical execution and task ownership",
        "mid": "mid-career, assessing architectural decisions and mentoring",
        "senior": "expert level, evaluating systems thinking and business impact",
        "lead": "leadership level, testing strategic vision and team scaling"
    }
    
    tech_str = ', '.join(keywords['technologies']) if keywords['technologies'] else 'the target tech stack'
    metrics_str = ', '.join(keywords['achievements']) if keywords['achievements'] else 'professional development'

    prompt = f"""
    ROLE: Expert Technical Recruiter for {position} ({seniority_level} level)
    TARGET FOCUS: {difficulty_map.get(seniority_level, 'general competence')}

    CANDIDATE RESUME CONTEXT:
    1. TECHNOLOGIES: {tech_str}
    2. KEY HIGHLIGHTS: {metrics_str}
    3. FULL RESUME CONTENT:
    \"\"\"
    {resume_text}
    \"\"\"

    TASK:
    Based on the resume content provided, generate exactly {num_questions} unique, challenging interview questions.

    STRICT GUIDELINES:
    - **Zero Generics**: DO NOT ask "Tell me about yourself" or "Why this company". 
    - **Code & Architecture Focus**: Reference a specific project, industry keyword, or achievement from the resume.
    - **Deep Personalization**: Every question must feel like you've deeply analyzed the candidate's background.
    - **No Defaults**: If the resume is sparse, ask high-level architectural questions about {position} best practices.
    - **Constraints**: 
      - Each question should be 20-40 words.
      - Return EXACTLY {num_questions} lines.
      - NO numbering, NO bolding, NO intro/outro.

    QUESTIONS:"""
    
    try:
        model = _get_model()
        response = model.generate_content(prompt, timeout=15)
        
        if response and response.text:
            raw_lines = response.text.strip().split('\n')
            questions = [re.sub(r'^[\d\.\-\*\s]+', '', line).strip() for line in raw_lines if len(line.strip()) > 15]
            if len(questions) >= 1:
                return questions[:int(num_questions)]
        
        return [f"Tell me about your experience with {tech_str.split(',')[0]} and how you used it in your projects."]
    except Exception as e:
        import sys
        print(f"❌ Question Gen Error: {e}", file=sys.stderr)
        # Better fallback: use the position and any tech found
        tech = tech_str.split(',')[0] if tech_str != 'the target tech stack' else position
        return [
            f"Can you describe a challenging project where you utilized your skills in {tech}?",
            f"Walk me through your technical implementation process for a {position} role.",
            f"What specific achievements in {tech} are you most proud of in your {seniority_level} career?"
        ][:int(num_questions)]


# =========================
# ⭐ FEEDBACK GENERATION
# =========================
def generate_feedback(question, answer):
    """
    Generate dual-perspective feedback (Recruiter vs Tech Lead).
    """
    if not answer or len(answer.strip()) < 10:
        return "⚠️ Your answer was too brief for a meaningful AI analysis. Try providing more context or examples."

    prompt = f"""
    INTERVIEW EVALUATION SYSTEM (Dual Perspective Mode):
    Question: {question}
    Candidate Answer: {answer}

    TASK: Provide an expert evaluation from two distinct viewpoints.

    FORMAT (Strictly follow this Markdown structure):

    ### 👤 THE RECRUITER (Perspective on Delivery & Impact)
    - **Strengths**: [What they did well in terms of confidence and soft skills]
    - **STAR Alignment**: [Did they follow Situation, Task, Action, Result?]
    - **Advice**: [How to make the answer more 'punchy' for a hiring manager]

    ---

    ### 💻 THE TECH LEAD (Perspective on Depth & Engineering)
    - **Technical Accuracy**: [Evaluation of the technical depth]
    - **Trade-offs**: [Did they mention alternate approaches or engineering trade-offs?]
    - **Optimization**: [Specific technical improvement or edge cases they missed]

    ---

    ### 📊 OVERALL PERFORMANCE
    - **Recruiter Rating**: [Score]/100
    - **Technical Rating**: [Score]/100
    - **Key Takeaway**: [One sentence final verdict]
    """

    try:
        model = _get_model()
        response = model.generate_content(prompt, timeout=15)
        if response and response.text:
            return response.text.strip()
        return "Feedback unavailable at the moment."
    except Exception as e:
        print(f"❌ Feedback Gen Error: {e}")
        return "Internal AI Error during evaluation."


# =========================
# 💡 GENERATE HINT
# =========================
def generate_hint(question, resume_text):
    """
    Generate a 1-sentence strategic hint for the candidate during the interview.
    """
    prompt = f"""
    Context: A candidate is answering this interview question: "{question}"
    Their Resume contains: "{resume_text[:1000]}"
    
    TASK: Provide a 1-sentence HINT to help them answer better. 
    Rule: Reference a specific tool or project from their resume that is relevant.
    Example: "Mention how you optimized the React state management in your E-commerce project."
    
    Return ONLY the 1-sentence hint.
    """
    try:
        model = _get_model()
        response = model.generate_content(prompt, timeout=10)
        return response.text.strip() if response else "Connect your answer to a specific project from your resume."
    except Exception:
        return "Connect your answer to a specific project from your resume."
