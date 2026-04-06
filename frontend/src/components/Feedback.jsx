'use client';

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const Feedback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Retrieve feedback data from navigation state.
  // Fallback dummy data provided for development.
  const feedback = location.state?.feedback || {
    transcript: "This is a sample transcript of your interview...",
    sentiment: { category: "Positive" },
    filler_counts: { um: 1, uh: 0, like: 2, "you know": 0, basically: 0, actually: 0 },
    audio_duration: 120,
    eye_contact_percentage: "85",
    average_confidence: 92,
    avg_sentence_length: "15 words",
    feedback: "Great clarity in your responses. Maintain eye contact for better engagement.",
    overall_score: 80, // Overall score from 0 to 100
  };

  const [showTranscript, setShowTranscript] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-purple-900 p-6 flex flex-col">
      {/* Page Header */}
      <header className="text-center mt-4">
        <h1 className="text-5xl font-extrabold text-white mb-2 tracking-wider">
          Your Interview Feedback
        </h1>
        <p className="text-lg text-gray-400 italic">
          A detailed breakdown of your performance.
        </p>
      </header>

      {/* Major Feedback Section */}
      <main className="flex-grow flex flex-col md:flex-row items-start justify-center mt-12 gap-8">
        {/* Left Column */}
        <div className="flex flex-col space-y-8 md:w-1/4">
          <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-blue-500 shadow-lg">
            <h2 className="text-2xl font-bold text-blue-300 mb-2">Tone</h2>
            <p className="text-xl text-gray-200">{feedback.sentiment}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-purple-500 shadow-lg">
            <h2 className="text-2xl font-bold text-purple-300 mb-2">Audio Duration</h2>
            <p className="text-xl text-gray-200">{feedback.audio_duration} sec</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-indigo-500 shadow-lg">
            <h2 className="text-2xl font-bold text-indigo-300 mb-2">Eye Contact</h2>
            <p className="text-xl text-gray-200">{feedback.eye_contact_percentage}%</p>
          </div>
        </div>

        {/* Center: Major Feedback with Overall Grade */}
        <div className="md:w-1/2 bg-gray-800 p-12 rounded-3xl shadow-2xl border border-gray-300 flex flex-col items-center">
          <div className="mb-8 flex flex-col items-center">
            <h2 className=" mb-8 text-4xl font-bold text-white ">Overall Grade</h2>
            <div className="w-40 h-40 font-bold">
              <CircularProgressbar
                value={parseInt(feedback.overall_score)}
                text={`${feedback.overall_score}%`}
                styles={buildStyles({
                  pathColor: '#10B981',   // Tailwind green-500
                  textColor: '#fff',
                  trailColor: '#4b5563',   // Tailwind gray-600
                  textSize: '20px',
                })}
              />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-100 mb-6 text-center">
            Major Feedback
          </h2>
          <p className="text-base text-gray-200 text-center whitespace-pre-wrap">
            {feedback.feedback}
          </p>
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            className="mt-6 px-4 py-2 bg-green-500 hover:bg-green-700 transition duration-200 font-bold text-white rounded-full shadow-lg"
          >
            {showTranscript ? "Hide Transcript" : "View Transcript"}
          </button>
          {showTranscript && (
            <div className="mt-6 w-full bg-gray-700 p-4 rounded-lg shadow">
              <h3 className="text-xl font-bold text-green-300 mb-2 text-center">Transcript</h3>
              <p className="text-sm text-gray-200 whitespace-pre-wrap text-center">
                {feedback.transcript}
              </p>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="flex flex-col space-y-8 md:w-1/4">
        <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-yellow-500 shadow-lg">
            <h2 className="text-2xl font-bold text-yellow-300 mb-2">Filler Word Count</h2>
            <ul className="text-xl text-gray-200 list-disc list-inside">
                {feedback.filler_counts &&
                (Object.entries(feedback.filler_counts)
                    .filter(([word, count]) => count > 0).length > 0 ? (
                    Object.entries(feedback.filler_counts)
                    .filter(([word, count]) => count > 0)
                    .map(([word, count]) => (
                        <li key={word}>
                        {word}: {count}
                        </li>
                    ))
                ) : (
                    <li>None</li>
                ))
                }
            </ul>
            </div>
          <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-pink-500 shadow-lg">
            <h2 className="text-2xl font-bold text-pink-300 mb-2">Average Confidence</h2>
            <p className="text-xl text-gray-200">{feedback.average_confidence}%</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-2xl border-l-4 border-red-500 shadow-lg">
            <h2 className="text-2xl font-bold text-red-300 mb-2">Average Sentence Length</h2>
            <p className="text-xl text-gray-200">{feedback.avg_sentence_length} words</p>
          </div>
        </div>
      </main>

      {/* Navigation Button */}
      <footer className="mt-12 flex justify-center">
        <button
          onClick={() => navigate('/practice')}
          className="px-8 py-3 bg-black hover:bg-red-700 transition duration-200 font-bold text-white rounded-full shadow-lg"
        >
          Next Question
        </button>
      </footer>
    </div>
  );
};

export default Feedback;