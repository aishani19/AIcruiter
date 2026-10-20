import os
from dotenv import load_dotenv
import re
from groq import Groq

# =========================
# 🔧 SETUP
# =========================
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

# 🔥 API KEY CHECK
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"⚠️ Groq client initialization warning: {e}")
else:
    print("⚠️ GROQ_API_KEY not found in .env")


def _get_client():
    global client
    if client:
        return client
    key = os.getenv("GROQ_API_KEY")
    if key:
        try:
            client = Groq(api_key=key)
            return client
        except Exception:
            pass
    return None


def _get_model():
    return os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


def _groq_chat_completion(messages, temperature=0.7, max_tokens=1024):
    c = _get_client()
    if not c:
        return None
    preferred = _get_model()
    candidates = [preferred, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    seen = set()
    for m in candidates:
        if not m or m in seen:
            continue
        seen.add(m)
        try:
            res = c.chat.completions.create(
                model=m,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            text = res.choices[0].message.content
            if text and text.strip():
                return text
        except Exception as e:
            print(f"⚠️ Groq completion failed on {m}: {e}")
            continue
    return None

try:
    from pdf_utils import extract_text_from_pdf
except ImportError:
    def extract_text_from_pdf(pdf_path):
        resume_text = ""
        try:
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
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
def generate_questions(resume_text, position, num_questions=5, seniority_level="fresher"):
    num_questions = int(num_questions) if num_questions else 5
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
    - Every line must be a completely distinct question.
    - NO numbering, NO bolding, NO intro/outro.
    - Each question 20-40 words.
    """
    
    response_text = _groq_chat_completion([{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1024)
    if response_text:
        raw_lines = response_text.strip().split('\n')
        cleaned = []
        seen = set()
        for line in raw_lines:
            q = re.sub(r'^\d+[\.\)\-]\s*', '', line.strip())
            q = q.strip(' *-"\'')
            if len(q) > 15 and q.lower() not in seen:
                seen.add(q.lower())
                cleaned.append(q)
        if len(cleaned) >= num_questions:
            return cleaned[:num_questions]
    
    # Rich diverse fallback questions
    diverse_fallbacks = [
        f"Walk me through a project from your resume where you applied {tech_str.split(',')[0]} to solve a concrete problem.",
        f"What architectural or design trade-offs did you consider when implementing your primary technical deliverables?",
        f"Describe a challenging bug or performance bottleneck you encountered as a {position} and how you diagnosed it.",
        f"How do you ensure test coverage, code reliability, and maintainability in your development workflow?",
        f"Can you discuss a time when project requirements changed rapidly and how you adjusted your engineering plan?",
        f"If you were to scale one of your resume projects to handle 10x the current load, what would you re-architect?",
        f"How do you stay current with new tools and best practices relevant to {position} roles?"
    ]
    return diverse_fallbacks[:num_questions]


# =========================
# ⭐ FEEDBACK GENERATION
# =========================
def generate_feedback(question, answer):
    if not answer or len(answer.strip()) < 10:
        return "⚠️ Your answer was too brief for a meaningful AI analysis. Please provide more context and specific examples."

    prompt = f"""
    INTERVIEW EVALUATION SYSTEM:
    Question: {question}
    Candidate Answer: {answer}

    TASK: Provide an expert evaluation from a Recruiter and Tech Lead perspective.
    Return Markdown format with sections: ### 👤 THE RECRUITER, ### 💻 THE TECH LEAD, ### 📊 OVERALL PERFORMANCE.
    """

    res = _groq_chat_completion([{"role": "user", "content": prompt}], temperature=0.5, max_tokens=1024)
    return res or "Feedback generation is temporarily unavailable. Good effort on your response!"


# =========================
# 💡 GENERATE HINT
# =========================
def generate_hint(question, resume_text=""):
    prompt = f"Provide a 1-sentence strategic hint (under 35 words) for this interview question: '{question}' based on this resume snippet: '{resume_text[:400]}'."
    res = _groq_chat_completion([{"role": "user", "content": prompt}], temperature=0.6, max_tokens=80)
    return res.strip() if res else "Connect your answer to a specific project from your resume and quantify your impact."

