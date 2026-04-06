import os
from dotenv import load_dotenv
import PyPDF2
import re
from groq import Groq

# =========================
# 🔧 SETUP
# =========================
load_dotenv()

# 🔥 API KEY CHECK
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("⚠️ GROQ_API_KEY not found in .env")


def _get_model():
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

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
# 🎯 QUESTION GENERATION
# =========================
def generate_questions(resume_text, position, num_questions, seniority_level="fresher"):
    if not client: return []
    
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
    - Return EXACTLY {num_questions} lines.
    - NO numbering, NO bolding, NO intro/outro.
    - Each question 20-40 words.
    """
    
    try:
        completion = client.chat.completions.create(
            model=_get_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        response_text = completion.choices[0].message.content
        if response_text:
            raw_lines = response_text.strip().split('\n')
            questions = [line.strip() for line in raw_lines if len(line.strip()) > 15]
            return questions[:int(num_questions)]
        
        return [f"Tell me about your experience with {tech_str.split(',')[0]}."]
    except Exception as e:
        print(f"❌ Groq Question Gen Error: {e}")
        return [f"Walk me through your technical process for a {position} role."]


# =========================
# ⭐ FEEDBACK GENERATION
# =========================
def generate_feedback(question, answer):
    if not client: return "Feedback unavailable."
    if not answer or len(answer.strip()) < 10:
        return "⚠️ Your answer was too brief for a meaningful AI analysis."

    prompt = f"""
    INTERVIEW EVALUATION SYSTEM:
    Question: {question}
    Candidate Answer: {answer}

    TASK: Provide an expert evaluation from a Recruiter and Tech Lead perspective.
    Return Markdown format with sections: ### 👤 THE RECRUITER, ### 💻 THE TECH LEAD, ### 📊 OVERALL PERFORMANCE.
    """

    try:
        completion = client.chat.completions.create(
            model=_get_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return completion.choices[0].message.content or "Feedback unavailable."
    except Exception as e:
        print(f"❌ Groq Feedback Error: {e}")
        return "Internal AI Error during evaluation."


# =========================
# 💡 GENERATE HINT
# =========================
def generate_hint(question, resume_text):
    if not client: return "Connect your answer to a specific project."
    prompt = f"Provide a 1-sentence strategic hint for this interview question: '{question}' based on this resume snippet: '{resume_text[:500]}'."
    try:
        completion = client.chat.completions.create(
            model=_get_model(),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return "Connect your answer to a specific project from your resume."
