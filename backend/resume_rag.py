import json
import os
import re
from collections import Counter

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY)


def _get_model():
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were",
    "with", "you", "your", "this", "their", "they", "them", "about",
    "into", "over", "under", "than", "then", "also", "have", "has", "had",
    "will", "would", "can", "could", "should", "may", "might", "i", "we",
}


def extract_resume_text(file_path):
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()

    if not text:
        raise ValueError("Could not extract any text from the uploaded PDF resume.")

    return text


def build_resume_summary(resume_text, max_points=5):
    lines = [line.strip(" -•\t") for line in resume_text.splitlines()]
    filtered = [line for line in lines if len(line) > 30]
    return filtered[:max_points]


def _extract_json_block(text):
    if not text:
        return ""

    fenced_match = re.search(r"```json\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1).strip()

    array_start = text.find("[")
    array_end = text.rfind("]")
    if array_start != -1 and array_end != -1 and array_end > array_start:
        return text[array_start:array_end + 1]

    object_start = text.find("{")
    object_end = text.rfind("}")
    if object_start != -1 and object_end != -1 and object_end > object_start:
        return text[object_start:object_end + 1]

    return text.strip()


def _parse_json_response(text, fallback):
    try:
        return json.loads(_extract_json_block(text))
    except Exception:
        return fallback


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
    score = 0
    for token in query_tokens:
        score += chunk_counter.get(token, 0)

    for bigram_index in range(len(query_tokens) - 1):
        phrase = f"{query_tokens[bigram_index]} {query_tokens[bigram_index + 1]}"
        if phrase in chunk.lower():
            score += 2

    return score


def retrieve_relevant_chunks(resume_text, query, top_k=3):
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


def _call_llm(prompt):
    try:
        completion = client.chat.completions.create(
            model=_get_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content or ""
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return ""


def _fallback_questions(relevant_chunks, role, num_questions):
    questions = []
    for index in range(num_questions):
        snippet = (relevant_chunks[index % len(relevant_chunks)][:180].strip() if relevant_chunks else "Resume project or experience")
        questions.append({
            "id": f"q-{index + 1}",
            "text": f"Can you walk me through a resume project or achievement that best prepares you for a {role} position?",
            "category": "resume-based",
            "focus_area": role or "general",
            "difficulty": "medium",
            "resume_reference": snippet,
            "why_asked": "This question is grounded in the candidate's resume content.",
        })
    return questions


def generate_questions_from_resume(resume_text, role, num_questions, level):
    relevant_chunks = retrieve_relevant_chunks(
        resume_text,
        f"{role} {level} projects skills impact leadership experience",
        top_k=4,
    )
    rag_context = "\n\n".join(
        [f"Resume excerpt {index + 1}: {chunk}" for index, chunk in enumerate(relevant_chunks)]
    )

    prompt = f"""
You are an expert interviewer creating personalized mock interview questions.

Target role: {role}
Seniority: {level}
Question count: {num_questions}

Ground every question in the resume evidence below.

{rag_context}

Return strict JSON only as an array with exactly {num_questions} objects.
Each object must include:
- id
- text
- category
- focus_area
- difficulty
- resume_reference
- why_asked

Rules:
- Mix technical, behavioral, and project deep-dive questions when possible.
- Make the questions feel tailored to the resume.
- Keep each question concise.
"""

    parsed = _parse_json_response(_call_llm(prompt), [])
    if not isinstance(parsed, list) or not parsed:
        return _fallback_questions(relevant_chunks, role, num_questions)

    normalized = []
    for index, item in enumerate(parsed[:num_questions]):
        if not isinstance(item, dict):
            continue
        normalized.append({
            "id": item.get("id") or f"q-{index + 1}",
            "text": item.get("text") or f"Question {index + 1}",
            "category": item.get("category") or "resume-based",
            "focus_area": item.get("focus_area") or (role or "general"),
            "difficulty": item.get("difficulty") or "medium",
            "resume_reference": item.get("resume_reference") or "",
            "why_asked": item.get("why_asked") or "",
        })

    if len(normalized) < num_questions:
        normalized.extend(_fallback_questions(relevant_chunks, role, num_questions - len(normalized)))

    return normalized[:num_questions]


def feedback_to_markdown(feedback_data):
    strengths = feedback_data.get("strengths") or ["No strengths identified."]
    weaknesses = feedback_data.get("weaknesses") or ["No weaknesses identified."]
    suggestions = feedback_data.get("suggestions") or ["No suggestions available."]
    ideal_points = feedback_data.get("ideal_points") or ["No ideal points available."]

    lines = [
        f"## Score: {feedback_data.get('score', 'N/A')}/100",
        "",
        "### Overall Feedback",
        feedback_data.get("overall_feedback", "No feedback generated."),
        "",
        "### Resume Alignment",
        feedback_data.get("resume_alignment", "No alignment summary available."),
        "",
        "### Strengths",
    ]
    lines.extend([f"- {item}" for item in strengths])
    lines.extend(["", "### Weaknesses"])
    lines.extend([f"- {item}" for item in weaknesses])
    lines.extend(["", "### Suggestions"])
    lines.extend([f"- {item}" for item in suggestions])
    lines.extend(["", "### Ideal Points To Cover"])
    lines.extend([f"- {item}" for item in ideal_points])

    evidence = feedback_data.get("referenced_resume_evidence")
    if evidence:
        lines.extend(["", "### Resume Evidence Used", evidence])

    return "\n".join(lines)


def _fallback_feedback(question, answer, relevant_chunks):
    evidence = relevant_chunks[0][:240].strip() if relevant_chunks else "No matching resume excerpt was found."
    return {
        "score": 65 if answer.strip() else 20,
        "strengths": ["You addressed the question directly."],
        "weaknesses": ["The answer needs more specific details, outcomes, and technical depth."],
        "suggestions": [
            "Use a STAR structure and include measurable results.",
            "Anchor your answer in a specific resume project or achievement.",
        ],
        "ideal_points": [
            "Clear project context",
            "Your responsibilities",
            "Technologies used",
            "Impact or result",
        ],
        "overall_feedback": f"The answer to '{question}' would be stronger with concrete examples and outcomes.",
        "resume_alignment": "Partial alignment with the resume context.",
        "referenced_resume_evidence": evidence,
    }


def generate_feedback(question, answer, resume_text=""):
    relevant_chunks = retrieve_relevant_chunks(resume_text, f"{question} {answer}", top_k=3)
    rag_context = "\n\n".join(
        [f"Resume excerpt {index + 1}: {chunk}" for index, chunk in enumerate(relevant_chunks)]
    ) or "No resume context available."

    prompt = f"""
You are an interview evaluator. Assess the answer using the question and the resume evidence.

Question:
{question}

Candidate answer:
{answer}

Resume evidence:
{rag_context}

Return strict JSON only with:
- score
- strengths
- weaknesses
- suggestions
- ideal_points
- overall_feedback
- resume_alignment
- referenced_resume_evidence

Rules:
- score must be an integer from 0 to 100.
- strengths, weaknesses, suggestions, and ideal_points must be arrays of short strings.
- Be constructive and specific.
"""

    parsed = _parse_json_response(_call_llm(prompt), {})
    if not isinstance(parsed, dict) or not parsed:
        parsed = _fallback_feedback(question, answer, relevant_chunks)

    feedback_data = {
        "score": int(parsed.get("score", 0) or 0),
        "strengths": parsed.get("strengths") if isinstance(parsed.get("strengths"), list) else [],
        "weaknesses": parsed.get("weaknesses") if isinstance(parsed.get("weaknesses"), list) else [],
        "suggestions": parsed.get("suggestions") if isinstance(parsed.get("suggestions"), list) else [],
        "ideal_points": parsed.get("ideal_points") if isinstance(parsed.get("ideal_points"), list) else [],
        "overall_feedback": "\n".join(parsed.get("overall_feedback")) if isinstance(parsed.get("overall_feedback"), list) else (parsed.get("overall_feedback") or ""),
        "resume_alignment": "\n".join(parsed.get("resume_alignment")) if isinstance(parsed.get("resume_alignment"), list) else (parsed.get("resume_alignment") or ""),
        "referenced_resume_evidence": "\n".join(parsed.get("referenced_resume_evidence")) if isinstance(parsed.get("referenced_resume_evidence"), list) else (parsed.get("referenced_resume_evidence") or ""),
    }
    feedback_data["markdown"] = feedback_to_markdown(feedback_data)
    return feedback_data


def generate_hint(question, resume_text=""):
    relevant_chunks = retrieve_relevant_chunks(resume_text, question, top_k=2)
    rag_context = "\n\n".join(relevant_chunks) or "No resume context available."

    prompt = f"""
Give a short helpful hint for answering this interview question.

Question:
{question}

Relevant resume context:
{rag_context}

Rules:
- Keep it under 60 words.
- Encourage the candidate to use a specific resume example.
"""

    response = _call_llm(prompt).strip()
    return response or "Use one specific resume example, explain your role, and end with the impact you created."
