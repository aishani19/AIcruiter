import React, { useEffect, useState } from 'react';
import Navbar from './Navbar';
import api from '../utils/api';
import LoadingSpinner from './LoadingSpinner';

const Leaderboard = () => {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await api.get('/leaderboard');
        setLeaders(response.data.leaderboard || []);
      } catch (err) {
        console.error('Failed to fetch leaderboard');
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  return (
    <div className="bg-gradient-to-b from-black via-gray-900 to-purple-900 min-h-screen text-white pt-24 font-sans">
      <Navbar />
      <div className="container mx-auto px-6 max-w-4xl">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500 mb-4 inline-block tracking-tight">
            Hall of Fame
          </h1>
          <p className="text-gray-400 text-lg font-medium">The world's most prepared candidates are here.</p>
        </div>

        <div className="bg-gray-900/50 backdrop-blur-2xl rounded-3xl border border-gray-800 shadow-2xl overflow-hidden p-1">
          {loading ? (
            <div className="flex justify-center items-center py-32">
              <LoadingSpinner />
            </div>
          ) : leaders.length === 0 ? (
            <div className="text-center py-24">
               <div className="text-6xl mb-4">🏆</div>
               <p className="text-gray-400 text-xl font-bold tracking-wide">Waiting for the first champions...</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {leaders.map((user, index) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-6 transition-all hover:bg-indigo-600/10 group"
                >
                  <div className="flex items-center gap-6">
                    <div
                      className={`flex items-center justify-center w-12 h-12 rounded-2xl font-black text-xl shadow-2xl transition-transform group-hover:scale-110 ${
                        index === 0
                          ? 'bg-yellow-500 text-black animate-pulse'
                          : index === 1
                          ? 'bg-gray-300 text-black'
                          : index === 2
                          ? 'bg-orange-500 text-black'
                          : 'bg-gray-800 text-indigo-400'
                      }`}
                    >
                      {index + 1}
                    </div>
                    <div>
                        <span className="font-bold text-xl block">{user.name}</span>
                        <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">{user.skill || 'Candidate'}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="flex items-center gap-2">
                       <span className="text-indigo-400 font-black text-3xl drop-shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                         {Math.round(user.score)}
                       </span>
                       <span className="text-gray-500 text-xs font-black tracking-tighter">XP</span>
                    </div>
                    <div className="text-[10px] text-green-500 font-bold uppercase tracking-widest mt-1">
                       Verified Skill
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="mt-12 text-center text-gray-500 text-sm font-medium">
           Score is calculated based on accuracy, tone, and confidence.
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
