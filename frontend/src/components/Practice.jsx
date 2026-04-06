import React, { useState, useEffect, useRef } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import { useNavigate, useLocation } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner';
import ReactMarkdown from 'react-markdown';
import api from '../utils/api';

const PracticeQuestion = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { questions, sessionId } = location.state || {};

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(questions?.[0]?.text || "");
  const [currentQuestionId, setCurrentQuestionId] = useState(questions?.[0]?.id || "");

  const [answerFormat, setAnswerFormat] = useState('text'); // 'text', 'video', 'audio'
  const [textAnswer, setTextAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [liveFeedback, setLiveFeedback] = useState(null);
  const [isLiveFeedbackLoading, setIsLiveFeedbackLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hint, setHint] = useState(null);
  const [isHintLoading, setIsHintLoading] = useState(false);

  const hasData = questions && questions.length > 0;

  // Recorders
  const videoRecorder = useReactMediaRecorder({ audio: true, video: true });
  const audioRecorder = useReactMediaRecorder({ audio: true });

  const activeRecorder = answerFormat === 'video' ? videoRecorder : audioRecorder;

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) navigate('/login');
  }, [navigate]);

  useEffect(() => {
    if (questions && currentQuestionIndex < questions.length) {
      const q = questions[currentQuestionIndex];
      setCurrentQuestion(q.text);
      setCurrentQuestionId(q.id);
      setTextAnswer('');
      setFeedback(null);
      setScore(null);
      setTranscript('');
      setAnalysis(null);
      setLiveFeedback(null);
      setHint(null);
    }
  }, [currentQuestionIndex, questions]);

  const getLiveFeedback = async () => {
    if (!textAnswer || textAnswer.trim().length < 20 || isLiveFeedbackLoading) return;
    setIsLiveFeedbackLoading(true);
    try {
      const response = await api.post('/realtime-feedback', {
        question: currentQuestion,
        answer_text: textAnswer
      });
      setLiveFeedback(response.data);
    } catch (err) {
      setLiveFeedback({ live_feedback: "Live feedback is unavailable right now." });
    } finally {
      setIsLiveFeedbackLoading(false);
    }
  };

  const fetchHint = async () => {
    if (isHintLoading) return;
    setIsHintLoading(true);
    try {
      const response = await api.post('/get-hint', { question: currentQuestion });
      setHint(response.data.hint);
    } catch (err) {
      setHint("Focus on a specific achievement from your resume.");
    } finally {
      setIsHintLoading(false);
    }
  };

  const handleSubmit = async () => {
    // Validate input based on format
    if (answerFormat === 'text') {
      // For text-only answers
      if (!textAnswer || textAnswer.trim().length < 10) {
        setFeedback("⚠️ Please type a detailed answer (at least 10 characters).");
        return;
      }
    } else if (answerFormat === 'video' || answerFormat === 'audio') {
      // For video/audio answers (text is optional)
      if (!activeRecorder.mediaBlobUrl) {
        setFeedback(`⚠️ Please record your ${answerFormat} answer first.`);
        return;
      }
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('question', currentQuestion);
      formData.append('question_id', currentQuestionId);
      formData.append('answer_text', textAnswer);
      formData.append('answerFormat', answerFormat);

      // 📥 Handle Media Blob
      if ((answerFormat === 'video' || answerFormat === 'audio') && activeRecorder.mediaBlobUrl) {
        try {
          const blob = await fetch(activeRecorder.mediaBlobUrl).then(r => {
            if (!r.ok) throw new Error('Failed to fetch media blob');
            return r.blob();
          });
          
          if (blob.size === 0) {
            throw new Error('Media blob is empty. Recording may have failed.');
          }
          
          formData.append('answer', blob, `answer_${Date.now()}.webm`);
        } catch (blobErr) {
          setFeedback(`⚠️ Media preparation failed: ${blobErr.message}`);
          setIsLoading(false);
          return;
        }
      }

      const response = await api.post('/submit-answer', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setFeedback(response.data.feedback);
      setScore(response.data.score);
      setTranscript(response.data.transcript || '');
      setAnalysis({
        confidenceScore: response.data.confidence_score,
        expressionScore: response.data.expression_score,
        framingScore: response.data.framing_score,
        expressionFeedback: response.data.expression_feedback,
        framingFeedback: response.data.framing_feedback
      });
    } catch (err) {
      console.error("Submit error:", err);
      const errorMsg = err.response?.data?.error || err.message || 'Unknown error occurred';
      setFeedback(`⚠️ Error: ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-900 to-gray-900 text-white flex items-center justify-center p-4">
      {isLoading && <LoadingSpinner />}

      {!hasData && (
        <div className="bg-gray-900 p-10 rounded-3xl text-center shadow-2xl border border-gray-800">
          <h2 className="text-red-400 text-xl mb-4 font-bold">Interview Session Expired</h2>
          <button onClick={() => navigate('/get-started')} className="bg-indigo-600 px-8 py-3 rounded-xl font-bold hover:bg-indigo-500 transition-all">
             Restart Session
          </button>
        </div>
      )}

      {hasData && (
        <div className="bg-gray-900/60 backdrop-blur-xl p-10 rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-800 shadow-2xl custom-scrollbar">
          
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-black text-indigo-400">Question {currentQuestionIndex + 1} <span className="text-gray-600 text-lg">/ {questions.length}</span></h2>
            <div className="flex gap-2">
               {['text', 'video', 'audio'].map(fmt => (
                 <button 
                  key={fmt} 
                  onClick={() => setAnswerFormat(fmt)}
                  className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${answerFormat === fmt ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-500 hover:text-gray-300'}`}
                 >
                   {fmt}
                 </button>
               ))}
            </div>
          </div>

          <div className="bg-gray-800/40 p-8 rounded-3xl border border-gray-700/50 mb-8 relative group backdrop-blur-sm">
            <p className="text-2xl leading-relaxed font-bold text-gray-100">{currentQuestion}</p>
            
            <button
              onClick={fetchHint}
              disabled={isHintLoading || feedback}
              className="absolute -bottom-4 right-8 bg-amber-500 hover:bg-amber-400 text-black px-6 py-2.5 rounded-full text-xs font-black shadow-xl transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
            >
              {isHintLoading ? "Analyzing..." : "💡 Get AI Hint"}
            </button>
          </div>

          {hint && (
            <div className="mb-8 animate-in slide-in-from-top fade-in duration-500 bg-amber-900/10 border border-amber-500/20 p-6 rounded-2xl text-amber-200 text-sm italic shadow-inner">
               <span className="font-black not-italic mr-2">PRO-TIP:</span> "{hint}"
            </div>
          )}

          {/* Media Section */}
          <div className="mb-8 space-y-6">
            {answerFormat !== 'text' && (
              <div className="bg-black/40 rounded-3xl p-6 border border-gray-800 flex flex-col items-center gap-6">
                 {answerFormat === 'video' && activeRecorder.previewStream && (
                   <video 
                     autoPlay 
                     muted 
                     ref={(video) => video && (video.srcObject = activeRecorder.previewStream)} 
                     className="w-full max-w-md aspect-video rounded-2xl border-2 border-indigo-600/30 bg-gray-900 shadow-2xl"
                   />
                 )}
                 
                 <div className="flex items-center gap-4">
                    {activeRecorder.status !== 'recording' ? (
                      <button 
                        onClick={activeRecorder.startRecording}
                        className="bg-red-600 hover:bg-red-500 px-8 py-3 rounded-full font-black text-sm uppercase tracking-widest transition-all shadow-lg shadow-red-600/20"
                      >
                         Record Answer
                      </button>
                    ) : (
                      <button 
                         onClick={activeRecorder.stopRecording}
                         className="bg-gray-100 text-black px-8 py-3 rounded-full font-black text-sm uppercase tracking-widest transition-all animate-pulse"
                      >
                         Stop Recording
                      </button>
                    )}
                    <span className="text-xs font-black text-gray-600 uppercase tracking-widest">{activeRecorder.status}</span>
                 </div>
              </div>
            )}

            <div className="relative">
               <label className="block text-xs font-black text-gray-600 uppercase tracking-widest mb-4">Transcript / Written Response</label>
               <textarea
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  className="w-full h-48 p-8 bg-gray-950/40 border border-gray-800 rounded-3xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder-gray-800 text-xl font-medium"
                  placeholder="Your answer will appear here if recording, or you can type it manually..."
               />
            </div>
            <button
              onClick={getLiveFeedback}
              disabled={isLiveFeedbackLoading || !textAnswer || textAnswer.trim().length < 20 || !!feedback}
              className="w-full py-3 bg-gray-800 hover:bg-gray-700 rounded-xl font-bold text-sm transition-all disabled:opacity-50"
            >
              {isLiveFeedbackLoading ? "Generating live coaching..." : "Get Instant AI Feedback"}
            </button>
            {liveFeedback?.live_feedback && !feedback && (
              <div className="bg-indigo-950/40 border border-indigo-600/30 rounded-2xl p-6">
                <p className="text-xs uppercase tracking-widest text-indigo-300 font-black mb-2">Live Feedback</p>
                <div className="prose prose-invert max-w-none text-sm">
                  <ReactMarkdown>{liveFeedback.live_feedback}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>

          {!feedback && (
            <button
              onClick={handleSubmit}
              disabled={isLoading || (!textAnswer && !activeRecorder.mediaBlobUrl)}
              className="w-full py-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-2xl font-black text-xl shadow-2xl shadow-indigo-600/20 transition-all active:scale-[0.99] disabled:opacity-50"
            >
              {isLoading ? "AI Analysis in Progress..." : "Submit for Expert Analysis"}
            </button>
          )}

          {feedback && (
            <div className="mt-12 animate-in slide-in-from-bottom duration-700">
              <div className="grid md:grid-cols-4 gap-3 mb-6">
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <p className="text-[10px] uppercase tracking-widest text-gray-400">Overall</p>
                  <p className="text-2xl font-black text-emerald-300">{score ?? "--"}</p>
                </div>
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <p className="text-[10px] uppercase tracking-widest text-gray-400">Confidence</p>
                  <p className="text-2xl font-black text-indigo-300">{analysis?.confidenceScore ?? "--"}</p>
                </div>
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <p className="text-[10px] uppercase tracking-widest text-gray-400">Expression</p>
                  <p className="text-2xl font-black text-purple-300">{analysis?.expressionScore ?? "--"}</p>
                </div>
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <p className="text-[10px] uppercase tracking-widest text-gray-400">Framing</p>
                  <p className="text-2xl font-black text-cyan-300">{analysis?.framingScore ?? "--"}</p>
                </div>
              </div>

              {transcript && (
                <div className="mb-6 bg-gray-950/60 border border-gray-800 rounded-2xl p-6">
                  <p className="text-[10px] uppercase tracking-widest text-gray-500 font-black mb-2">Auto Transcript</p>
                  <p className="text-gray-300 text-sm leading-relaxed">{transcript}</p>
                </div>
              )}

              {(analysis?.expressionFeedback || analysis?.framingFeedback) && (
                <div className="mb-8 grid md:grid-cols-2 gap-4">
                  <div className="bg-purple-950/30 border border-purple-700/30 rounded-2xl p-5">
                    <p className="text-xs uppercase tracking-widest text-purple-300 font-black mb-2">Expression Coaching</p>
                    <p className="text-sm text-purple-100">{analysis?.expressionFeedback}</p>
                  </div>
                  <div className="bg-cyan-950/30 border border-cyan-700/30 rounded-2xl p-5">
                    <p className="text-xs uppercase tracking-widest text-cyan-300 font-black mb-2">Answer Framing Coaching</p>
                    <p className="text-sm text-cyan-100">{analysis?.framingFeedback}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-4 mb-8">
                <div className="w-14 h-14 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center text-3xl shadow-xl shadow-indigo-600/30">✨</div>
                <div>
                   <h3 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-purple-200">Expert Panel Evaluation</h3>
                   <p className="text-[10px] text-gray-500 uppercase font-black tracking-[0.3em]">AI Career Intelligence System</p>
                </div>
              </div>

              <div className="bg-gray-950/60 border-l-4 border-indigo-600 p-10 rounded-r-[2.5rem] rounded-bl-[2.5rem] backdrop-blur-2xl shadow-inner border-y border-r border-gray-800/50">
                 <div className="prose prose-invert max-w-none feedback-panel text-gray-300 leading-relaxed">
                    <ReactMarkdown>{feedback}</ReactMarkdown>
                 </div>
              </div>

              <button
                onClick={handleNextQuestion}
                className="mt-10 w-full py-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-2xl font-black text-xl shadow-2xl active:scale-[0.99] transition-all"
              >
                {currentQuestionIndex < questions.length - 1 ? "Next Challenge →" : "Finalize Session"}
              </button>
            </div>
          )}

        </div>
      )}
    </div>
  );
};

export default PracticeQuestion;
