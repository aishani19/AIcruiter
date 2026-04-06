import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import 'react-circular-progressbar/dist/styles.css';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    user_name: 'User',
    avg_score: 0,
    total_interviews: 0,
    bar_data: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/dashboard-stats');
        setStats(response.data);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const progress = stats.avg_score;

  // Real data from backend
  const displayBarData = stats.bar_data && stats.bar_data.length > 0 
    ? stats.bar_data 
    : [{ name: 'No Data', score: 0 }];

  const displayPieData = stats.pie_data && stats.pie_data.length > 0
    ? stats.pie_data
    : [
        { name: 'Eye Contact', value: 25 },
        { name: 'Confidence', value: 40 },
        { name: 'Tone', value: 20 },
        { name: 'Length', value: 15 },
      ];

  const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#8b5cf6'];

  return (
    <div className="bg-gradient-to-t from-black via-gray-900 to-purple-900 min-h-screen text-white text-center">
      <Navbar />
      <div className="container mx-auto px-6 pt-32 pb-10">
        {/* Header Row: Welcome Message & Action Button */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
          <div className="lg:col-span-2 flex flex-col justify-center text-left">
            <h1 className="text-6xl lg:text-7xl font-black mb-3 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500 tracking-tight">
              Welcome Back {stats.user_name}!
            </h1>
            <p className="text-xl lg:text-2xl text-gray-400 mb-8 max-w-2xl font-medium">
              You have completed <span className="text-indigo-400 font-bold">{stats.total_interviews}</span> mock interviews. Your consistency is paying off.
            </p>
            <div className="flex justify-start">
              <button
                onClick={() => navigate('/get-started')}
                className="group relative px-10 py-5 bg-indigo-600 hover:bg-indigo-500 transition-all text-xl text-white font-black rounded-2xl shadow-2xl shadow-indigo-600/20 active:scale-95"
              >
                <span className="flex items-center gap-2">
                   Launch Practice Session <span className="group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </button>
            </div>

          </div>
          {/* Overall Score Card */}
          <div className="flex items-center justify-center">
            <div className="bg-gray-900/60 backdrop-blur-xl p-8 rounded-3xl border border-gray-800 shadow-2xl w-full max-w-xs text-center">
              <div className="w-32 h-32 mx-auto mb-4">
                <CircularProgressbar
                  value={progress}
                  text={`${progress}%`}
                  styles={buildStyles({
                    textColor: '#fff',
                    pathColor: '#6366f1',
                    trailColor: '#1f2937',
                    strokeLinecap: 'round'
                  })}
                />
              </div>
              <h2 className="text-gray-400 font-bold uppercase tracking-widest text-[10px] mb-1">
                Average Score
              </h2>
              <div className="text-indigo-400 font-black text-xl">Interview Readiness</div>
            </div>
          </div>
        </div>

        {/* Metrics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Past Interview Scores Graph */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 text-white">
              Past Interview Scores
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={displayBarData}>
                <XAxis dataKey="name" stroke="#6366f1" />
                <YAxis stroke="#6366f1" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '12px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Areas of Improvement Pie Chart */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 text-white">
              Areas of Improvement
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={displayPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  innerRadius={50}
                  fill="#a855f7"
                  stroke="none"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {displayPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10">
          {/* View Past Interviews */}
          <div
            onClick={() => navigate('/history')}
            className="cursor-pointer bg-gray-800/40 border border-gray-700 rounded-3xl shadow-lg p-8 hover:border-indigo-500/50 transition-all group"
          >
            <h3 className="text-xl font-semibold text-white mb-2">View Past Interviews</h3>
            <p className="text-gray-400">
              Review your previous practice sessions and feedback.
            </p>
          </div>

          {/* Next Steps */}
          <div
            onClick={() => navigate('/dashboard')}
            className="cursor-pointer bg-gray-800 rounded-lg shadow-lg p-6 hover:bg-gray-700 transition"
          >
            <h3 className="text-xl font-semibold text-white mb-2">Next Steps</h3>
            <p className="text-gray-400">
              Get personalized guidance on improving your interview skills.
            </p>
          </div>
        </div>

        {/* Additional Features (Dynamic) */}
        <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Achievements */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Recent Achievements</h3>
            <div className="flex justify-between">
              <div className="bg-indigo-600 rounded-lg shadow-inner p-4 text-center flex-1 mx-1">
                <p className="text-2xl font-bold">{stats.achievements?.completed || 0}</p>
                <p className="text-gray-300 text-xs">Sessions</p>
              </div>
              <div className="bg-purple-600 rounded-lg shadow-inner p-4 text-center flex-1 mx-1">
                <p className="text-2xl font-bold">{stats.achievements?.targets_met || 0}</p>
                <p className="text-gray-300 text-xs">Targets Met</p>
              </div>
              <div className="bg-fuchsia-600 rounded-lg shadow-inner p-4 text-center flex-1 mx-1">
                <p className="text-2xl font-bold">{stats.achievements?.skills_improved || 0}</p>
                <p className="text-gray-300 text-xs">Skills Boosted</p>
              </div>
            </div>
          </div>

          {/* Upcoming Goals */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">AI Recommended Goals</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-300 text-left">
              {(stats.upcoming_goals && stats.upcoming_goals.length > 0) ? (
                stats.upcoming_goals.map((goal, idx) => (
                  <li key={idx} className="hover:text-indigo-400 transition-colors">{goal}</li>
                ))
              ) : (
                <li>Start your first interview to get AI-generated goals!</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;