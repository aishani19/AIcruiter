from sqlalchemy import (
    Column, Integer, String, Float, Text, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False, server_default='password')
    resume_path = Column(String(500), nullable=True)  # Path to the PDF file
    total_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interview_sessions = relationship("InterviewSession", back_populates="user")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    desired_occupation = Column(String(255), nullable=True)
    num_questions = Column(Integer, nullable=False)
    seniority_level = Column(String(50), default="fresher", nullable=False)  # fresher, junior, mid, senior, lead
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("Question", back_populates="session")


class Question(Base):
    __tablename__ = "questions"
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.session_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    audio_path = Column(Text, nullable=True)  # Path to audio file of the question
    order = Column(Integer, nullable=False)
    difficulty = Column(String(50), default="medium", nullable=False)  # easy, medium, hard
    
    session = relationship("InterviewSession", back_populates="questions")
    response = relationship("Response", back_populates="question", uselist=False)


class Response(Base):
    __tablename__ = "responses"
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.question_id"), nullable=True)
    answer_type = Column(String(20), default='video')  # 'video', 'audio', 'text'
    video_path = Column(Text, nullable=True)
    audio_path = Column(Text, nullable=True)
    text_answer = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    question = relationship("Question", back_populates="response")
    evaluation_metrics = relationship("EvaluationMetrics", back_populates="response", uselist=False)


class EvaluationMetrics(Base):
    __tablename__ = "evaluation_metrics"
    
    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(Integer, ForeignKey("responses.response_id"), nullable=False)
    wpm = Column(Float, nullable=True)
    eye_contact = Column(Float, nullable=True)
    filler_words_count = Column(Integer, nullable=True)
    avg_sentence_length = Column(Float, nullable=True)
    avg_loudness = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    question_relevance_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    
    response = relationship("Response", back_populates="evaluation_metrics")
