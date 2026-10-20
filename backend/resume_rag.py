import json
import os
import re
import random
from collections import Counter
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

# ==========================================
# 📄 PDF UTILS IMPORT
# ==========================================
try:
    from pdf_utils import extract_text_from_pdf
except ImportError:
    from pypdf import PdfReader
    def extract_text_from_pdf(path):
        try:
            reader = PdfReader(path)
            return "\n".join([p.extract_text() or "" for p in reader.pages]).strip()
        except Exception:
            return ""

def extract_resume_text(file_path):
    text = extract_text_from_pdf(file_path)
    if not text or "unavailable" in text.lower():
        raise ValueError("Could not extract any text from the uploaded PDF resume.")
    return text

# ==========================================
# 🤖 MULTI-PROVIDER LLM CLIENT (GROQ + GEMINI)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_groq_client = None
def _get_groq_client():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=api_key)
            return _groq_client
        except Exception as e:
            print(f"⚠️ Groq client initialization warning: {e}")
    return None

_gemini_configured = False
def _get_gemini_model():
    global _gemini_configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        if not _gemini_configured:
            genai.configure(api_key=api_key)
            _gemini_configured = True
        preferred = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        candidates = [preferred, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for name in candidates:
            if not name:
                continue
            try:
                return genai.GenerativeModel(name)
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ Gemini client warning: {e}")
    return None

def _call_llm(prompt, temperature=0.75):
    """
    Robust dual-provider LLM caller.
    Attempts Groq first; if Groq hits 429 rate limit or network issues,
    seamlessly falls back to Gemini.
    """
    # 1. Try Groq
    groq_client = _get_groq_client()
    if groq_client:
        groq_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        groq_candidates = [groq_model, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        seen_models = set()
        for m in groq_candidates:
            if not m or m in seen_models:
                continue
            seen_models.add(m)
            try:
                completion = groq_client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=2048,
                )
                content = completion.choices[0].message.content or ""
                if content.strip():
                    return content.strip()
            except Exception as e:
                err_str = str(e).lower()
                print(f"⚠️ Groq attempt with {m} failed: {e}")
                # If rate limited (429), break immediately to avoid waiting and switch to Gemini
                if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                    break
                continue

    # 2. Seamless Fallback to Gemini
    gemini_model = _get_gemini_model()
    if gemini_model:
        try:
            res = gemini_model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            if res and res.text and res.text.strip():
                return res.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini fallback failed: {e}")

    return ""


# ==========================================
# 🔍 RESUME ANALYSIS & KEYWORDS
# ==========================================
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were",
    "with", "you", "your", "this", "their", "they", "them", "about",
    "into", "over", "under", "than", "then", "also", "have", "has", "had",
    "will", "would", "can", "could", "should", "may", "might", "i", "we",
}

def extract_resume_entities(resume_text):
    """
    Extracts key technologies and notable project/achievement keywords.
    """
    if not resume_text or "unavailable" in resume_text.lower():
        return {"technologies": [], "achievements": []}

    tech_catalog = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby", "swift",
        "react", "angular", "vue", "next.js", "nextjs", "node.js", "nodejs", "express", "django", "flask",
        "fastapi", "spring boot", "spring", "docker", "kubernetes", "aws", "azure", "gcp",
        "postgresql", "postgres", "mongodb", "mysql", "redis", "sqlite", "graphql", "rest", "restful",
        "git", "ci/cd", "microservices", "kafka", "rabbitmq", "tailwind", "redux", "pandas", "numpy",
        "tensorflow", "pytorch", "scikit-learn", "linux", "jenkins", "terraform", "sql", "html", "css"
    ]
    resume_lower = resume_text.lower()
    found_tech = []
    for tech in tech_catalog:
        if re.search(r'\b' + re.escape(tech) + r'\b', resume_lower):
            display = tech.title() if len(tech) > 3 else tech.upper()
            if display not in found_tech:
                found_tech.append(display)

    achievements = re.findall(
        r'(\d+(?:%|\+|\s*(?:years?|projects?|users?|months?|clients?|revenue|stars?|ms|seconds?)))',
        resume_lower
    )

    return {
        "technologies": found_tech,
        "achievements": list(set(achievements))[:6]
    }

def _tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9+#.]+", (text or "").lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]

def _chunk_resume_text(resume_text, chunk_size=900, overlap=180):
    clean_text = re.sub(r"\s+", " ", (resume_text or "")).strip()
    if not clean_text:
        return []
    chunks = []
    start = 0
    while start < len(clean_text):
        end = min(len(clean_text), start + chunk_size)
        chunks.append(clean_text[start:end].strip())
        if end >= len(clean_text):
            break
        start = max(0, end - overlap)
    return chunks

def _score_chunk(chunk, query_tokens):
    if not chunk or not query_tokens:
        return 0
    chunk_counter = Counter(_tokenize(chunk))
    score = sum(chunk_counter.get(token, 0) for token in query_tokens)
    for i in range(len(query_tokens) - 1):
        phrase = f"{query_tokens[i]} {query_tokens[i + 1]}"
        if phrase in chunk.lower():
            score += 2
    return score

def retrieve_relevant_chunks(resume_text, query, top_k=4):
    chunks = _chunk_resume_text(resume_text)
    if not chunks:
        return []
    query_tokens = _tokenize(query)
    ranked = []
    for index, chunk in enumerate(chunks):
        ranked.append((_score_chunk(chunk, query_tokens), index, chunk))
    ranked.sort(key=lambda item: (item[0], -len(item[2])), reverse=True)
    top_chunks = [chunk for score, _, chunk in ranked[:top_k] if score > 0]
    return top_chunks or chunks[:top_k]


# ==========================================
# 🧩 ROBUST JSON & TEXT PARSER
# ==========================================
def _clean_llm_text(text):
    if not text:
        return ""
    # Strip <think> tags from reasoning models
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()

def _extract_json_block(text):
    cleaned = _clean_llm_text(text)
    if not cleaned:
        return ""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    array_start = cleaned.find("[")
    array_end = cleaned.rfind("]")
    if array_start != -1 and array_end != -1 and array_end > array_start:
        return cleaned[array_start:array_end + 1]
    obj_start = cleaned.find("{")
    obj_end = cleaned.rfind("}")
    if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
        return cleaned[obj_start:obj_end + 1]
    return cleaned

def _parse_questions_output(raw_text):
    """
    Parses LLM response regardless of format:
    1. JSON array of objects ([{text/question: ...}])
    2. JSON array of strings (["Q1", "Q2"])
    3. JSON dict containing an array ({"questions": [...]})
    4. Plain text numbered/bulleted lines (1. ..., 2. ...)
    """
    questions = []
    cleaned_text = _clean_llm_text(raw_text)
    json_str = _extract_json_block(cleaned_text)

    # Attempt 1: Parse JSON
    if json_str:
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                # Look for array in dict keys
                for key in ["questions", "interview_questions", "items", "data", "questions_list"]:
                    if key in parsed and isinstance(parsed[key], list):
                        parsed = parsed[key]
                        break
                else:
                    # Look for first list value in dict
                    for val in parsed.values():
                        if isinstance(val, list):
                            parsed = val
                            break

            if isinstance(parsed, list):
                for item in parsed:
                    q_text = ""
                    difficulty = "medium"
                    category = "technical"
                    if isinstance(item, dict):
                        q_text = (
                            item.get("text")
                            or item.get("question")
                            or item.get("q")
                            or item.get("prompt")
                            or item.get("title")
                            or ""
                        ).strip()
                        difficulty = item.get("difficulty", "medium")
                        category = item.get("category", "technical")
                    elif isinstance(item, str):
                        q_text = item.strip()

                    if q_text and len(q_text) > 15:
                        questions.append({
                            "text": q_text,
                            "difficulty": difficulty,
                            "category": category
                        })
        except Exception:
            pass

    # Attempt 2: If JSON parsing gave no questions, parse plain text / markdown lines
    if not questions and cleaned_text:
        lines = cleaned_text.splitlines()
        for line in lines:
            line_str = line.strip()
            # Match 1. Question, Q1: Question, - Question, * Question
            match = re.match(r'^(?:\d+[\.\)\-]|Q\d+[:.-]?|[-*•])\s*(.+)$', line_str, re.IGNORECASE)
            candidate = match.group(1).strip() if match else line_str
            candidate = candidate.strip(' *-"\'')
            if len(candidate) > 20 and not candidate.lower().startswith(("here are", "sure,", "questions:", "mock interview")):
                questions.append({
                    "text": candidate,
                    "difficulty": "medium",
                    "category": "technical"
                })

    return questions


# ==========================================
# 🎯 DYNAMIC RESUME-GROUNDED FALLBACK
# ==========================================
def _fallback_questions(relevant_chunks, role, num_questions, resume_text=""):
    """
    Creates dynamic, personalized fallback questions referencing candidate's
    actual technologies and background so it NEVER repeats identical questions.
    """
    entities = extract_resume_entities(resume_text or " ".join(relevant_chunks))
    techs = entities.get("technologies", [])
    achievements = entities.get("achievements", [])
    role_title = role or "Software Engineer"

    # Dynamic tech anchors
    t1 = techs[0] if len(techs) > 0 else "core backend services"
    t2 = techs[1] if len(techs) > 1 else (techs[0] if techs else "the frontend stack")
    t3 = techs[2] if len(techs) > 2 else "database and caching"

    pool = [
        {
            "category": "technical",
            "focus_area": "core_competencies",
            "difficulty": "medium",
            "text": f"Walk me through a project from your resume where you applied {t1}. What architectural choices did you make and what were your specific contributions?",
            "why_asked": f"To test hands-on mastery in {t1}."
        },
        {
            "category": "architecture",
            "focus_area": "system_design",
            "difficulty": "hard",
            "text": f"Looking at your experience with {t1} and {t2}, how did you ensure seamless data flow, state consistency, and API reliability between them?",
            "why_asked": "To evaluate integration and architectural judgment."
        },
        {
            "category": "problem-solving",
            "focus_area": "debugging",
            "difficulty": "hard",
            "text": f"Tell me about a complex technical blocker or performance bottleneck you diagnosed in your work. What tools and telemetry did you use to find the root cause?",
            "why_asked": "To assess debugging methodology under pressure."
        },
        {
            "category": "database_and_scaling",
            "focus_area": "data_engineering",
            "difficulty": "hard",
            "text": f"How did you approach data modeling and query optimization with {t3} in your implementations? How would you handle a 10x traffic spike?",
            "why_asked": "To test data architecture and scalability awareness."
        },
        {
            "category": "quality_and_reliability",
            "focus_area": "production_standards",
            "difficulty": "medium",
            "text": f"What testing strategy, CI/CD patterns, and code review practices do you follow to ensure high production quality in a {role_title} role?",
            "why_asked": "To assess engineering discipline and production readiness."
        },
        {
            "category": "behavioral",
            "focus_area": "adaptability",
            "difficulty": "medium",
            "text": f"Describe a situation where project specifications changed unexpectedly or you had to adopt an unfamiliar framework on short notice. How did you navigate the delivery?",
            "why_asked": "To measure agility, fast learning curve, and communication."
        },
        {
            "category": "trade-offs",
            "focus_area": "pragmatic_engineering",
            "difficulty": "hard",
            "text": f"Can you give an example of an engineering trade-off you navigated—such as delivery speed vs tech debt, or caching vs data consistency?",
            "why_asked": "To assess pragmatic balance in engineering decisions."
        },
        {
            "category": "security_and_resilience",
            "focus_area": "security",
            "difficulty": "medium",
            "text": f"How do you safeguard user authentication, sensitive credentials, and prevent common vulnerabilities across your {role_title} applications?",
            "why_asked": "To verify proactive security awareness."
        }
    ]

    # Shuffle to ensure dynamic order on subsequent generations
    random.shuffle(pool)

    out = []
    seen = set()
    for item in pool:
        q_text = item["text"].strip()
        if q_text.lower() not in seen:
            seen.add(q_text.lower())
            out.append({
                "id": f"q-{len(out) + 1}",
                "text": q_text,
                "category": item["category"],
                "focus_area": item["focus_area"],
                "difficulty": item["difficulty"],
                "resume_reference": t1,
                "why_asked": item["why_asked"]
            })
            if len(out) >= num_questions:
                break

    return out[:num_questions]


# ==========================================
# 🚀 GENERATE QUESTIONS FROM RESUME
# ==========================================
def generate_questions_from_resume(resume_text, role, num_questions=5, level="fresher"):
    """
    Main question generation entry point.
    Extracts resume context, queries LLM (Groq with Gemini failover),
    robustly parses diverse output formats, and returns distinct personalized questions.
    """
    num_questions = int(num_questions) if num_questions else 5
    role_title = role or "Software Engineer"
    
    # Extract entities and relevant excerpts
    entities = extract_resume_entities(resume_text)
    tech_str = ", ".join(entities["technologies"][:8]) if entities["technologies"] else "standard engineering tools"
    
    relevant_chunks = retrieve_relevant_chunks(
        resume_text,
        f"{role_title} {level} projects skills impact technologies experience",
        top_k=4,
    )
    rag_context = "\n\n".join(
        [f"Resume Excerpt {index + 1}: {chunk}" for index, chunk in enumerate(relevant_chunks)]
    ) if relevant_chunks else (resume_text[:2000] if resume_text else "General candidate background.")

    # Dynamic seed / focus to encourage fresh questions each time
    perspectives = [
        "architecture and real-world system design",
        "deep technical debugging and edge-case handling",
        "hands-on project implementation and individual contributions",
        "scalability, performance optimization, and testing"
    ]
    chosen_focus = random.choice(perspectives)

    prompt = f"""
You are an expert technical interviewer conducting a mock interview for a {role_title} ({level} level).
Special focus for this interview round: {chosen_focus}.

CANDIDATE RESUME EVIDENCE:
Technologies identified: {tech_str}

{rag_context}

TASK:
Generate exactly {num_questions} unique, challenging, and insightful interview questions grounded directly in the candidate's actual projects, tools, and background.

CRITICAL RULES:
- Ground every question in specific skills or projects from their resume.
- NO generic or repetitive questions.
- Every question MUST be unique and completely distinct from all others.
- Keep each question between 20 and 45 words.
- Return ONLY valid JSON as an array of {num_questions} objects.
- Each object MUST have:
  - "text": The complete question string.
  - "difficulty": "easy", "medium", or "hard".
  - "category": "technical", "system_design", "debugging", or "behavioral".

Example JSON format:
[
  {{
    "text": "In your resume, you built an API using {tech_str.split(',')[0].strip()}. How did you handle validation, errors, and database connection pooling?",
    "difficulty": "medium",
    "category": "technical"
  }}
]
"""

    raw_response = _call_llm(prompt, temperature=0.82)
    parsed_questions = _parse_questions_output(raw_response)

    normalized = []
    seen_texts = set()

    for item in parsed_questions:
        q_text = (item.get("text") or "").strip()
        q_lower = q_text.lower()
        if not q_text or q_lower in seen_texts or len(q_text) < 15:
            continue
        seen_texts.add(q_lower)
        normalized.append({
            "id": f"q-{len(normalized) + 1}",
            "text": q_text,
            "category": item.get("category", "technical"),
            "focus_area": role_title,
            "difficulty": item.get("difficulty", "medium"),
            "resume_reference": tech_str,
            "why_asked": f"To assess practical depth in {role_title} competencies."
        })
        if len(normalized) == num_questions:
            break

    # If LLM didn't return enough distinct questions, complement with dynamic fallback
    if len(normalized) < num_questions:
        needed = num_questions - len(normalized)
        fallbacks = _fallback_questions(relevant_chunks, role_title, needed * 2, resume_text=resume_text)
        for fb in fallbacks:
            fb_lower = fb["text"].lower()
            if fb_lower not in seen_texts:
                seen_texts.add(fb_lower)
                fb["id"] = f"q-{len(normalized) + 1}"
                normalized.append(fb)
                if len(normalized) == num_questions:
                    break

    return normalized[:num_questions]


# ==========================================
# 📊 FEEDBACK EVALUATION
# ==========================================
def feedback_to_markdown(feedback_data):
    strengths = feedback_data.get("strengths") or ["Clear and relevant explanation."]
    weaknesses = feedback_data.get("weaknesses") or ["Could include more specific metrics or outcomes."]
    suggestions = feedback_data.get("suggestions") or ["Use the STAR framework (Situation, Task, Action, Result)."]
    ideal_points = feedback_data.get("ideal_points") or ["Specific technology choices and measurable results."]

    lines = [
        f"## Score: {feedback_data.get('score', '75')}/100",
        "",
        "### Overall Feedback",
        feedback_data.get("overall_feedback", "Solid attempt. Good domain context provided."),
        "",
        "### Resume Alignment",
        feedback_data.get("resume_alignment", "Aligned with candidate technical background."),
        "",
        "### Strengths",
    ]
    lines.extend([f"- {item}" for item in strengths])
    lines.extend(["", "### Areas for Improvement"])
    lines.extend([f"- {item}" for item in weaknesses])
    lines.extend(["", "### Actionable Suggestions"])
    lines.extend([f"- {item}" for item in suggestions])
    lines.extend(["", "### Ideal Points To Cover"])
    lines.extend([f"- {item}" for item in ideal_points])

    evidence = feedback_data.get("referenced_resume_evidence")
    if evidence:
        lines.extend(["", "### Resume Evidence Anchor", evidence])

    return "\n".join(lines)


def _fallback_feedback(question, answer, relevant_chunks):
    evidence = relevant_chunks[0][:240].strip() if relevant_chunks else "Candidate resume context."
    score = 75 if len(answer.strip()) > 50 else (60 if answer.strip() else 25)
    return {
        "score": score,
        "strengths": ["You addressed the core technical theme of the question."],
        "weaknesses": ["Consider adding measurable outcomes, metrics, or specific architectural decisions."],
        "suggestions": [
            "Structure your answer using the STAR method: Situation, Task, Action, Result.",
            "Cite a concrete project from your resume to substantiate your technical claim."
        ],
        "ideal_points": [
            "Context and problem statement",
            "Technical tools and implementation details",
            "Measurable impact or key takeaways"
        ],
        "overall_feedback": f"Your response to '{question[:60]}...' demonstrates foundational knowledge. Quantifying your impact will make it significantly more persuasive.",
        "resume_alignment": "Demonstrates alignment with your technical experience.",
        "referenced_resume_evidence": evidence,
    }


def generate_feedback(question, answer, resume_text=""):
    relevant_chunks = retrieve_relevant_chunks(resume_text, f"{question} {answer}", top_k=3)
    rag_context = "\n\n".join(
        [f"Resume excerpt {index + 1}: {chunk}" for index, chunk in enumerate(relevant_chunks)]
    ) or "No resume context available."

    prompt = f"""
You are an expert interview evaluator and senior hiring manager.
Assess the candidate's answer to the given interview question.

Question:
{question}

Candidate Answer:
{answer}

Resume Evidence:
{rag_context}

Return strict JSON only with:
{{
  "score": <integer from 0 to 100>,
  "strengths": [<array of 2-3 specific strength strings>],
  "weaknesses": [<array of 1-3 constructive critique strings>],
  "suggestions": [<array of 2 actionable advice strings>],
  "ideal_points": [<array of 3 key points a top-tier candidate would mention>],
  "overall_feedback": "<2-3 sentence executive evaluation>",
  "resume_alignment": "<1-2 sentence assessment of how well it maps to their resume>",
  "referenced_resume_evidence": "<short resume excerpt or project reference>"
}}
"""

    raw = _call_llm(prompt, temperature=0.5)
    parsed = {}
    json_str = _extract_json_block(raw)
    if json_str:
        try:
            parsed = json.loads(json_str)
        except Exception:
            pass

    if not isinstance(parsed, dict) or "score" not in parsed:
        parsed = _fallback_feedback(question, answer, relevant_chunks)

    score_val = parsed.get("score", 70)
    try:
        score_int = int(score_val)
    except Exception:
        score_int = 70

    feedback_data = {
        "score": max(0, min(100, score_int)),
        "strengths": parsed.get("strengths") if isinstance(parsed.get("strengths"), list) else ["Clear technical explanation."],
        "weaknesses": parsed.get("weaknesses") if isinstance(parsed.get("weaknesses"), list) else ["Include more quantifiable outcomes."],
        "suggestions": parsed.get("suggestions") if isinstance(parsed.get("suggestions"), list) else ["Anchor answers with concrete project examples."],
        "ideal_points": parsed.get("ideal_points") if isinstance(parsed.get("ideal_points"), list) else ["System trade-offs and performance impact."],
        "overall_feedback": "\n".join(parsed.get("overall_feedback")) if isinstance(parsed.get("overall_feedback"), list) else (parsed.get("overall_feedback") or "Good technical response."),
        "resume_alignment": "\n".join(parsed.get("resume_alignment")) if isinstance(parsed.get("resume_alignment"), list) else (parsed.get("resume_alignment") or "Relevant to resume background."),
        "referenced_resume_evidence": "\n".join(parsed.get("referenced_resume_evidence")) if isinstance(parsed.get("referenced_resume_evidence"), list) else (parsed.get("referenced_resume_evidence") or ""),
    }
    feedback_data["markdown"] = feedback_to_markdown(feedback_data)
    return feedback_data


# ==========================================
# 💡 GENERATE HINT
# ==========================================
def generate_hint(question, resume_text=""):
    relevant_chunks = retrieve_relevant_chunks(resume_text, question, top_k=2)
    rag_context = "\n\n".join(relevant_chunks) if relevant_chunks else "Candidate technical experience."

    prompt = f"""
Give a concise, high-impact hint (under 40 words) for answering this interview question:
Question: {question}
Resume context: {rag_context}

Rule: Encourage the candidate to reference a concrete technical project or tool from their background.
"""
    response = _call_llm(prompt, temperature=0.6).strip()
    # Strip any extra quotes or preambles
    response = re.sub(r'^(?:Hint:\s*|["\'])', '', response).rstrip('"\'')
    return response or "Anchor your answer in a specific project from your resume, detailing your exact contributions and impact."
