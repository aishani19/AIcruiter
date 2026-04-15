import logging
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, func
import sqlalchemy
from sqlalchemy import inspect, text
from models import InterviewSession, Question, User, Response, EvaluationMetrics
from sqlalchemy.orm import sessionmaker, scoped_session
import time
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import bcrypt
import jwt
import re
from datetime import datetime, timedelta
from functools import wraps



# Fix Windows encoding issues
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Set UTF-8 as default for file operations
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ✅ Core AI & Media Imports
from groq_api import extract_text_from_pdf
from resume_rag import (
    generate_questions_from_resume,
    generate_feedback as generate_rag_feedback,
    generate_hint as generate_rag_hint,
)
from audio_transcription import process_user_video

# Helper function for text sanitization
def sanitize_text(text):
    """Remove problematic unicode characters that cause encoding issues on Windows"""
    if not text:
        return ""
    try:
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        return text.strip()
    except:
        return text

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")}})

import secrets as _secrets
_secret_key = os.getenv('SECRET_KEY')
if not _secret_key:
    logger.warning("SECRET_KEY not set — generating a random ephemeral key. Set SECRET_KEY env var in production!")
    _secret_key = _secrets.token_hex(32)
app.config['SECRET_KEY'] = _secret_key

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alcruiter.db")

# DB Setup
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("SELECT 1"))
    logger.info("✓ Connected to PostgreSQL")
except:
    DATABASE_URL = "sqlite:///./alcruiter.db"
    engine = create_engine(DATABASE_URL, echo=False)
    logger.info("✓ Using SQLite database")

Session = scoped_session(sessionmaker(bind=engine))

import models
models.Base.metadata.create_all(engine)
logger.info("✓ Database schema verified")




def ensure_runtime_schema():
    """
    Lightweight runtime schema patching for existing DBs created by older app versions.
    """
    inspector = inspect(engine)
    with engine.begin() as conn:
        # responses.feedback
        if "responses" in inspector.get_table_names():
            response_columns = {col["name"] for col in inspector.get_columns("responses")}
            if "feedback" not in response_columns:
                conn.execute(text("ALTER TABLE responses ADD COLUMN feedback TEXT"))
                logger.info("✓ Added missing column responses.feedback")

        # evaluation_metrics newly used fields
        if "evaluation_metrics" in inspector.get_table_names():
            metric_columns = {col["name"] for col in inspector.get_columns("evaluation_metrics")}
            metric_additions = [
                ("wpm", "FLOAT"),
                ("eye_contact", "FLOAT"),
                ("filler_words_count", "INTEGER"),
                ("avg_sentence_length", "FLOAT"),
                ("avg_loudness", "FLOAT"),
                ("duration", "FLOAT"),
                ("question_relevance_score", "FLOAT"),
                ("overall_score", "FLOAT"),
            ]
            for col_name, col_type in metric_additions:
                if col_name not in metric_columns:
                    conn.execute(text(f"ALTER TABLE evaluation_metrics ADD COLUMN {col_name} {col_type}"))
                    logger.info(f"✓ Added missing column evaluation_metrics.{col_name}")


try:
    ensure_runtime_schema()
except Exception as schema_err:
    logger.warning(f"Schema patch skipped: {schema_err}")

# Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            db_session = Session()
            current_user = db_session.query(User).filter_by(user_id=data['user_id']).first()
            db_session.close()
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return jsonify({'error': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# =========================
# 🔥 AUTH ENDPOINTS
# =========================
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return jsonify({"error": "Email already exists"}), 400
        
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_pw)
        session.add(new_user)
        session.commit()
        
        token = jwt.encode({"user_id": new_user.user_id, "exp": datetime.utcnow() + timedelta(days=7)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token, "user": {"id": new_user.user_id, "name": new_user.name}}), 201
    finally:
        session.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401

        token = jwt.encode({"user_id": user.user_id, "exp": datetime.utcnow() + timedelta(days=7)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token, "user": {"id": user.user_id, "name": user.name}}), 200
    finally:
        session.close()


# =========================
# 🧠 GENERATE QUESTIONS API
# =========================
@app.route('/api/generate-questions', methods=['POST'])
@token_required
def generate_questions_api(current_user):
    try:
        file = request.files.get('resume')
        occupation = request.form.get('occupation')
        num_questions = int(request.form.get('num_questions', 5))
        seniority = request.form.get('seniority_level', 'fresher')

        if not file:
            return jsonify({"error": "No resume uploaded"}), 400

        # Validate num_questions to prevent abuse (excessive API calls)
        num_questions = max(1, min(num_questions, 20))

        # Validate seniority level
        VALID_SENIORITY = {"fresher", "junior", "mid", "senior", "lead"}
        if seniority not in VALID_SENIORITY:
            seniority = "fresher"

        # Validate file type
        ALLOWED_EXTENSIONS = {'.pdf'}
        _, ext = os.path.splitext(file.filename or '')
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Only PDF files are accepted"}), 400

        # Validate file size (max 10 MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10 MB limit"}), 400

        # Save resume path to user
        file_path = os.path.join(UPLOAD_FOLDER, f"user_{current_user.user_id}_resume.pdf") 
        file.save(file_path)
        
        db_session = Session()
        try:
            # Update user resume path
            db_session.query(User).filter(User.user_id == current_user.user_id).update({"resume_path": file_path})
            
            # Create Interview Session
            interview_session = InterviewSession(
                user_id=current_user.user_id,
                desired_occupation=occupation,
                num_questions=num_questions,
                seniority_level=seniority
            )
            db_session.add(interview_session)
            db_session.flush()

            # Process AI questions using resume-grounded RAG
            resume_text = extract_text_from_pdf(file_path)
            generated_list = generate_questions_from_resume(
                resume_text=resume_text,
                role=occupation or "Software Engineer",
                num_questions=num_questions,
                level=seniority,
            )
            
            logger.info(f"✓ AI generated {len(generated_list)} questions for session {interview_session.session_id}")
            
            if not generated_list:
                logger.warning(f"⚠️ AI returned 0 questions for session {interview_session.session_id}. Check Groq logs.")
                # Fallback handled in resume_rag, but if it still returns empty...

            formatted_questions = []
            for i, q_item in enumerate(generated_list):
                q_text = q_item.get("text") if isinstance(q_item, dict) else str(q_item)
                q_model = Question(
                    session_id=interview_session.session_id,
                    question_text=q_text,
                    order=i,
                    difficulty="medium"
                )
                db_session.add(q_model)
                db_session.flush()
                formatted_questions.append({
                    "id": q_model.question_id,
                    "text": q_text
                })

            db_session.commit()
            return jsonify({
                "questions": formatted_questions,
                "session_id": interview_session.session_id
            }), 200

        except Exception as e:
            db_session.rollback()
            logger.error(f"Question generation error: {e}", exc_info=True)
            return jsonify({"error": "An internal error occurred while generating questions."}), 500
        finally:
            db_session.close()

    except Exception as e:
        logger.error(f"Question generation error (outer): {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 🔥 SUBMIT ANSWER (FULL MEDIA SUPPORT)
# =========================
@app.route('/api/submit-answer', methods=['POST'])
@token_required
def submit_answer(current_user):
    try:
        db_session = Session()
        try:
            # Detect JSON or Form Data
            if request.is_json:
                data = request.json
                q_id = int(data.get('question_id')) if data.get('question_id') else None
                question_text = data.get('question')
                text_answer = data.get('answer_text')
                answer_format = "text"
                answer_file = None
            else:
                q_id = int(request.form.get('question_id')) if request.form.get('question_id') else None
                question_text = request.form.get('question')
                text_answer = request.form.get('answer_text', '')
                answer_format = request.form.get('answerFormat', 'video')
                answer_file = request.files.get('answer')

            # Initialize Response Variables
            video_path, audio_path = None, None
            transcript = text_answer
            ai_feedback = ""
            score = 70
            media_metrics = {}

            # 🎥 Handle Video/Audio Blob
            if answer_file:
                try:
                    filename = secure_filename(f"{answer_format}_{int(time.time())}.webm")
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    answer_file.save(file_path)
                    logger.info(f"✓ Saved {answer_format} file: {file_path}")
                    
                    if answer_format == 'video': 
                        video_path = file_path
                    else: 
                        audio_path = file_path
                    
                    # Use powerful audio_transcription engine
                    try:
                        logger.info(f"Starting media processing for {answer_format}...")
                        result = process_user_video([question_text], file_path)
                        
                        transcript = result.get('transcript', text_answer)
                        # Sanitize transcript to avoid encoding issues
                        transcript = sanitize_text(transcript) if transcript else text_answer
                        
                        if not transcript or transcript.strip() == '':
                            logger.warning("Transcription returned empty, using text answer")
                            transcript = text_answer or "No response provided"
                        
                        # Join metrics feedback with AI deep dive
                        feedback_list = result.get('feedback', [])
                        if isinstance(feedback_list, list):
                            ai_feedback = "\n\n".join(str(f) for f in feedback_list)
                        else:
                            ai_feedback = result.get('feedback', "")
                        
                        score = result.get('overall_score', 70)
                        
                        media_metrics = {
                            "wpm": result.get("wpm", 0),
                            "eye_contact": result.get("eye_contact_percentage", 0),
                            "filler_words_count": sum((result.get("filler_counts") or {}).values()),
                            "avg_sentence_length": result.get("avg_sentence_length", 0),
                            "duration": result.get("audio_duration", 0),
                            "confidence_score": result.get("confidence_score", 55),
                            "expression_score": result.get("expression_score", 55),
                            "framing_score": result.get("framing_score", 40),
                            "expression_feedback": result.get("expression_feedback", ""),
                            "framing_feedback": result.get("framing_feedback", ""),
                        }
                        logger.info(f"✓ Media processing complete. Score: {score}, Transcript length: {len(transcript)}")
                    except Exception as media_err:
                        logger.error(f"Media processing failed: {media_err}", exc_info=True)
                        ai_feedback = "Media processing error. Please try again."
                        score = 60
                except Exception as file_err:
                    logger.error(f"File handling error: {file_err}", exc_info=True)
                    ai_feedback = "File upload error. Please try again."
                    score = 55

            # ✍️ Fallback to RAG text evaluation if no AI feedback yet or insufficient metrics
            if not ai_feedback or score < 50:
                try:
                    logger.info("Attempting RAG-based text evaluation...")
                    user = db_session.query(User).filter_by(user_id=current_user.user_id).first()
                    resume_text = extract_text_from_pdf(user.resume_path) if user and user.resume_path else ""
                    rag_feedback = generate_rag_feedback(question_text or "", transcript or "", resume_text=resume_text)
                    
                    if ai_feedback:
                        ai_feedback = ai_feedback + "\n\n---\n\n" + rag_feedback.get("markdown", "")
                    else:
                        ai_feedback = rag_feedback.get("markdown", "Feedback unavailable.")
                    
                    if score < 50:
                        score = int(rag_feedback.get("score", 75))
                    logger.info(f"✓ RAG evaluation complete. Score: {score}")
                except Exception as rag_err:
                    logger.error(f"RAG feedback generation failed: {rag_err}", exc_info=True)
                    if not ai_feedback:
                        ai_feedback = "Unable to generate detailed feedback. Please try again."

            # Ensure minimum feedback quality
            if not ai_feedback or ai_feedback.strip() == '':
                ai_feedback = "Your response was recorded. For better feedback, please ensure your audio/video is clear and your answer is detailed."

            # 💾 Verify if q_id exists for data integrity
            valid_q_id = None
            if q_id:
                q_exists = db_session.query(Question).filter_by(question_id=q_id).first()
                if q_exists:
                    valid_q_id = q_id
                else:
                    logger.warning(f"⚠️ question_id {q_id} not found in DB. Saving response as unlinked.")

            # 💾 Save Response to DB
            resp = Response(
                question_id=valid_q_id,
                answer_type=answer_format,
                text_answer=text_answer,
                transcript=transcript,
                video_path=video_path,
                audio_path=audio_path,
                feedback=ai_feedback
            )
            db_session.add(resp)
            db_session.flush()

            # 💾 Save Metrics
            metrics = EvaluationMetrics(
                response_id=resp.response_id,
                wpm=media_metrics.get("wpm"),
                eye_contact=media_metrics.get("eye_contact"),
                filler_words_count=media_metrics.get("filler_words_count"),
                avg_sentence_length=media_metrics.get("avg_sentence_length"),
                duration=media_metrics.get("duration"),
                overall_score=score
            )
            db_session.add(metrics)
            
            db_session.commit()
            logger.info(f"✓ Response saved for user {current_user.user_id} with score {score}")
            
            return jsonify({
                "feedback": ai_feedback,
                "score": score,
                "transcript": transcript,
                "confidence_score": media_metrics.get("confidence_score"),
                "expression_score": media_metrics.get("expression_score"),
                "framing_score": media_metrics.get("framing_score"),
                "expression_feedback": media_metrics.get("expression_feedback"),
                "framing_feedback": media_metrics.get("framing_feedback"),
            }), 200

        except Exception as e:
            db_session.rollback()
            logger.error(f"Submit error inner: {e}", exc_info=True)
            return jsonify({"error": "An internal error occurred while processing your answer."}), 500
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Submit error outer: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 💡 GET HINT
# =========================
@app.route('/api/get-hint', methods=['POST'])
@token_required
def get_hint_api(current_user):
    try:
        data = request.json
        q_text = data.get('question')
        
        db_session = Session()
        try:
            user = db_session.query(User).filter_by(user_id=current_user.user_id).first()
            if not user or not user.resume_path:
                return jsonify({"hint": "Reference your core strengths or a major project achievement."}), 200
            
            resume_text = extract_text_from_pdf(user.resume_path)
            hint = generate_rag_hint(q_text, resume_text)
            return jsonify({"hint": hint}), 200
        finally:
            db_session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/realtime-feedback', methods=['POST'])
@token_required
def realtime_feedback_api(current_user):
    """Quick draft feedback while candidate is framing an answer."""
    try:
        data = request.json or {}
        question = (data.get("question") or "").strip()
        draft_answer = (data.get("answer_text") or "").strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400
        if len(draft_answer) < 20:
            return jsonify({
                "live_feedback": "Add more specifics. Mention one project, your exact role, and a measurable outcome.",
                "score": 0
            }), 200

        db_session = Session()
        try:
            user = db_session.query(User).filter_by(user_id=current_user.user_id).first()
            resume_text = extract_text_from_pdf(user.resume_path) if user and user.resume_path else ""
            rag_feedback = generate_rag_feedback(question, draft_answer, resume_text=resume_text)
            return jsonify({
                "live_feedback": rag_feedback.get("markdown", "Feedback unavailable."),
                "score": rag_feedback.get("score", 0),
                "resume_alignment": rag_feedback.get("resume_alignment", "")
            }), 200
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Realtime feedback error: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 📊 DASHBOARD STATS
# =========================
@app.route('/api/dashboard-stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    try:
        db_session = Session()
        try:
            # Total Interviews
            total_interviews = db_session.query(InterviewSession).filter_by(user_id=current_user.user_id).count()
            
            # Avg Score
            all_scores = db_session.query(EvaluationMetrics.overall_score).join(Response).join(Question).join(InterviewSession).filter(InterviewSession.user_id == current_user.user_id).all()
            avg_score = round(sum(s[0] for s in all_scores) / len(all_scores), 1) if all_scores else 0
            
            # Bar Data (Historical Scores)
            sessions = db_session.query(InterviewSession).filter_by(user_id=current_user.user_id).order_by(InterviewSession.created_at.asc()).all()
            bar_data = []
            for s in sessions[-5:]:
                s_scores = db_session.query(EvaluationMetrics.overall_score).join(Response).join(Question).filter(Question.session_id == s.session_id).all()
                s_avg = sum(sc[0] for sc in s_scores) / len(s_scores) if s_scores else 0
                bar_data.append({"name": s.created_at.strftime("%b %d"), "score": round(s_avg, 1)})
            
            # 🥧 Calculate Dynamic Pie Data (Averages across all sessions)
            # Fetch all metrics for the user
            metrics_list = db_session.query(EvaluationMetrics).join(Response).join(Question).join(InterviewSession).filter(InterviewSession.user_id == current_user.user_id).all()
            
            if metrics_list:
                avg_eye = sum((m.eye_contact or 0) for m in metrics_list) / len(metrics_list)
                avg_relevance = sum((m.question_relevance_score or 70) for m in metrics_list) / len(metrics_list)
                
                # Pacing Score: Normalize WPM (Ideal range 110-150)
                tot_pacing = 0
                for m in metrics_list:
                    wpm = m.wpm or 130
                    if 110 <= wpm <= 150: score_p = 90
                    elif wpm < 80 or wpm > 180: score_p = 50
                    else: score_p = 75
                    tot_pacing += score_p
                avg_pacing = tot_pacing / len(metrics_list)
                
                # Communication: Derived from filler words and overall
                avg_comm = sum((m.overall_score or 70) for m in metrics_list) / len(metrics_list)
                
                # Normalize values to sum to reasonable parts for a Pie Chart (or just use absolute averages)
                pie_data = [
                    {"name": "STAR Method", "value": round(avg_relevance, 1)},
                    {"name": "Eye Contact", "value": round(avg_eye, 1) or 20}, # Minimum slice for visibility
                    {"name": "Pacing", "value": round(avg_pacing, 1)},
                    {"name": "Accuracy", "value": round(avg_comm, 1)}
                ]
            else:
                pie_data = [
                    {"name": "STAR Method", "value": 0},
                    {"name": "Eye Contact", "value": 0},
                    {"name": "Pacing", "value": 0},
                    {"name": "Accuracy", "value": 0}
                ]
            
            # AI Goals
            goals = ["Complete 3 more practice sessions to improve STAR alignment."]
            if avg_score > 0 and avg_score < 70: 
                goals.append("Focus on providing more concrete examples in your answers.")
            elif avg_score >= 70:
                goals.append("Great job! Try a 'Mock Interview with Stress' mode to further hone your skills.")
            
            return jsonify({
                "user_name": current_user.name,
                "avg_score": avg_score,
                "total_interviews": total_interviews,
                "bar_data": bar_data,
                "pie_data": pie_data,
                "achievements": {"completed": total_interviews, "targets_met": len([s for s in all_scores if s[0] >= 85])},
                "upcoming_goals": goals
            }), 200
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 👤 INTERVIEW HISTORY
# =========================
@app.route('/api/history', methods=['GET'])
@token_required
def get_history(current_user):
    try:
        db_session = Session()
        try:
            sessions = db_session.query(InterviewSession).filter_by(user_id=current_user.user_id).order_by(InterviewSession.created_at.desc()).all()
            history = []
            for s in sessions:
                s_scores = db_session.query(EvaluationMetrics.overall_score).join(Response).join(Question).filter(Question.session_id == s.session_id).all()
                s_avg = sum(sc[0] for sc in s_scores) / len(s_scores) if s_scores else 0
                history.append({
                    "session_id": s.session_id,
                    "occupation": s.desired_occupation,
                    "seniority": s.seniority_level,
                    "created_at": s.created_at.strftime("%Y-%m-%d %H:%M"),
                    "avg_score": round(s_avg, 1)
                })
            return jsonify(history), 200
        finally:
            db_session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<int:session_id>', methods=['GET'])
@token_required
def get_session_detail_api(current_user, session_id):
    try:
        db_session = Session()
        try:
            session_obj = db_session.query(InterviewSession).filter_by(session_id=session_id, user_id=current_user.user_id).first()
            if not session_obj: return jsonify({"error": "Session not found"}), 404
            
            questions = db_session.query(Question).filter_by(session_id=session_id).order_by(Question.order).all()
            details = []
            for q in questions:
                resp = db_session.query(Response).filter_by(question_id=q.question_id).first()
                metrics = db_session.query(EvaluationMetrics).filter_by(response_id=resp.response_id).first() if resp else None
                details.append({
                    "question": q.question_text,
                    "answer": resp.text_answer if resp else "No answer recorded",
                    "feedback": resp.feedback if resp else "N/A",
                    "score": metrics.overall_score if metrics else 0
                })
            return jsonify({
                "occupation": session_obj.desired_occupation,
                "seniority": session_obj.seniority_level,
                "details": details
            }), 200
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Session detail error: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 🏆 LEADERBOARD
# =========================
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard_api():
    try:
        db_session = Session()
        try:
            users = db_session.query(User).all()
            leaderboard = []
            for u in users:
                s_scores = db_session.query(EvaluationMetrics.overall_score).join(Response).join(Question).join(InterviewSession).filter(InterviewSession.user_id == u.user_id).all()
                if not s_scores: continue
                u_avg = sum(sc[0] for sc in s_scores) / len(s_scores)
                leaderboard.append({
                    "id": u.user_id,
                    "name": u.name,
                    "score": round(u_avg * 10, 1),
                    "skill": "Elite" if u_avg > 85 else "Practitioner"
                })
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            return jsonify({"leaderboard": leaderboard[:10]}), 200
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Leaderboard error: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


# =========================
# 🧪 HEALTH
# =========================
@app.route('/api/test')
def test():
    return "API FULLY RESTORED ✅"

@app.route('/')
def home():
    return "Alcruiter Backend 🚀"


if __name__ == '__main__':
    # Disable reloader to prevent multiple server instances binding the same port on Windows.
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)