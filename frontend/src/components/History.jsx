import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from './LoadingSpinner';
import Navbar from './Navbar';

const History = () => {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get('/history');
        setSessions(response.data);
      } catch (err) {
        console.error("History fetch error:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-900 to-gray-900 text-white">
      <Navbar />
      <div className="container mx-auto px-6 pt-24 pb-12">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
              Interview History
            </h1>
            <p className="text-gray-400 mt-2">Track your growth and review past AI feedback.</p>
          </div>
          <button 
            onClick={() => navigate('/get-started')}
            className="bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-indigo-600/20"
          >
            + New Mock Interview
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <LoadingSpinner />
          </div>
        ) : sessions.length === 0 ? (
          <div className="bg-gray-800/50 border border-gray-700 rounded-3xl p-20 text-center backdrop-blur-sm">
            <div className="text-6xl mb-4">📝</div>
            <h2 className="text-2xl font-bold mb-2">No sessions yet</h2>
            <p className="text-gray-400 mb-8">Start your first interview to see history here.</p>
            <button 
              onClick={() => navigate('/get-started')}
              className="bg-indigo-600 px-8 py-3 rounded-xl font-bold"
            >
              Get Started
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {sessions.map((session) => (
              <div 
                key={session.session_id}
                onClick={() => navigate(`/history/${session.session_id}`)}
                className="group relative bg-[#0f172a]/40 hover:bg-[#1e293b]/60 border border-slate-800 hover:border-indigo-500/50 rounded-[2rem] p-8 cursor-pointer transition-all duration-500 backdrop-blur-xl hover:shadow-[0_20px_50px_rgba(79,70,229,0.15)] hover:-translate-y-2 overflow-hidden"
              >
                {/* Decorative background glow */}
                <div className="absolute -right-10 -top-10 w-32 h-32 bg-indigo-600/10 blur-3xl group-hover:bg-indigo-600/20 transition-all rounded-full"></div>
                
                <div className="flex justify-between items-start mb-6">
                  <div className="bg-slate-900/80 border border-slate-800 text-indigo-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] shadow-inner">
                    {session.seniority}
                  </div>
                  <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-500 group-hover:from-indigo-400 group-hover:to-purple-400 transition-all duration-500">
                    {session.avg_score}<span className="text-xs text-slate-600 ml-1 font-bold">/100</span>
                  </div>
                </div>
                
                <h3 className="text-2xl font-black mb-2 text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-indigo-300 transition-all truncate">
                  {session.occupation}
                </h3>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-8 flex items-center gap-2">
                  <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                  {session.created_at}
                </p>
                
                <div className="flex items-center justify-between pt-6 border-t border-slate-800/50">
                   <div className="flex flex-col">
                      <span className="text-[10px] text-slate-500 font-black uppercase tracking-tighter mb-0.5">Progress</span>
                      <div className="text-sm text-slate-300 font-bold">
                        <span className="text-indigo-400 font-black">{session.response_count}</span>
                        <span className="text-slate-600 mx-1">/</span>
                        {session.question_count} <span className="text-[10px] text-slate-500">Units</span>
                      </div>
                   </div>
                   <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white group-hover:border-indigo-500 transition-all duration-300">
                     <span className="text-xl">→</span>
                   </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
