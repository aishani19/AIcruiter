import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from './LoadingSpinner';
import Navbar from './Navbar';
import ReactMarkdown from 'react-markdown';

const SessionDetail = () => {
  const { sessionId } = useParams();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const response = await api.get(`/history/${sessionId}`);
        setData(response.data);
      } catch (err) {
        console.error("Session detail fetch error:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetail();
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center">
        <h2 className="text-2xl font-bold mb-4">Session Not Found</h2>
        <button onClick={() => navigate('/history')} className="bg-indigo-600 px-6 py-2 rounded">
          Back to History
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white pb-20">
      <Navbar />
      <div className="container mx-auto px-6 pt-24 max-w-5xl">
        <div className="flex items-center gap-4 mb-8">
           <button 
             onClick={() => navigate('/history')}
             className="p-2 hover:bg-gray-800 rounded-full text-indigo-400"
           >
             ← Back
           </button>
           <div>
             <h1 className="text-3xl font-bold">{data.occupation} <span className="text-indigo-400/60 font-normal">Details</span></h1>
             <p className="text-gray-500 font-medium tracking-wide uppercase text-xs mt-1">{data.seniority} • {data.created_at}</p>
           </div>
        </div>

        <div className="space-y-8">
          {data.details.map((item, idx) => (
            <div key={idx} className="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden shadow-2xl transition-all hover:border-indigo-500/20">
              <div className="p-6 border-b border-gray-800 flex justify-between items-center bg-gray-900/50">
                 <div className="flex items-center gap-3 font-bold text-indigo-300">
                   <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">Q{idx + 1}</div>
                   Question
                 </div>
                 <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 uppercase font-black">Score</span>
                    <span className="text-xl font-black text-indigo-400">{item.score}/100</span>
                 </div>
              </div>
              
              <div className="p-8">
                 <div className="text-xl leading-relaxed text-gray-200 mb-6 p-6 bg-gray-800/40 rounded-2xl border border-gray-700/30">
                   {item.question}
                 </div>

                 {/* Granular Metrics Bar */}
                 <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                   <div className="bg-gray-950/50 p-4 rounded-xl border border-gray-800">
                     <div className="text-[10px] text-gray-500 uppercase font-black mb-1">Eye Contact</div>
                     <div className="text-lg font-bold text-white">{item.eye_contact}%</div>
                   </div>
                   <div className="bg-gray-950/50 p-4 rounded-xl border border-gray-800">
                     <div className="text-[10px] text-gray-500 uppercase font-black mb-1">Speaking Rate</div>
                     <div className="text-lg font-bold text-white">{item.wpm} <span className="text-[10px]">wpm</span></div>
                   </div>
                   <div className="bg-gray-950/50 p-4 rounded-xl border border-gray-800">
                     <div className="text-[10px] text-gray-500 uppercase font-black mb-1">Fillers Count</div>
                     <div className="text-lg font-bold text-white">{item.fillers}</div>
                   </div>
                   <div className="bg-gray-950/50 p-4 rounded-xl border border-gray-800">
                     <div className="text-[10px] text-gray-500 uppercase font-black mb-1">Duration</div>
                     <div className="text-lg font-bold text-white">Analyzed</div>
                   </div>
                 </div>
                 
                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                       <h3 className="text-xs uppercase font-black text-gray-500 tracking-widest mb-4 flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Your Answer
                       </h3>
                       <div className="p-6 bg-gray-950 rounded-2xl border border-gray-800 text-gray-400 text-sm italic leading-relaxed min-h-[150px]">
                         {item.answer || "No text provided (Video/Audio only)"}
                       </div>
                    </div>
                    
                    <div>
                       <h3 className="text-xs uppercase font-black text-indigo-500 tracking-widest mb-4 flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span> AI Insights
                       </h3>
                       <div className="p-6 bg-indigo-900/10 rounded-2xl border border-indigo-500/20 text-indigo-100 prose prose-invert max-w-none text-sm/relaxed feedback-detail">
                         <ReactMarkdown>{item.feedback}</ReactMarkdown>
                       </div>
                    </div>
                 </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SessionDetail;
