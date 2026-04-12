import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from './Navbar';
import api from '../utils/api';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem('token')) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const endpoint = isLogin ? '/login' : '/signup';
    const payload = isLogin ? { email, password } : { name, email, password };

    try {
      const response = await api.post(endpoint, payload);
      const data = response.data;

      if (data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError('Unexpected response from server.');
      }
    } catch (err) {
      console.error("❌ ERROR:", err);
      const rawError = err.response?.data?.error || err.response?.data || err.message || "Failed to generate questions.";
      setError(typeof rawError === "string" ? rawError : (rawError.message || JSON.stringify(rawError)));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-purple-900 flex flex-col">
      <Navbar />
      <section className="flex-grow flex items-center justify-center pt-20 p-4">
        <div className="w-full max-w-md">
          <div className="bg-gray-900/60 backdrop-blur-2xl rounded-3xl shadow-2xl border border-gray-800 p-10 overflow-hidden relative">
            
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

            <div className="text-center mb-10">
              <div className="text-6xl mb-6 animate-bounce-slow">
                {isLogin ? '🔐' : '✨'}
              </div>
              <h1 className="text-4xl font-black text-white tracking-tight mb-2">
                {isLogin ? 'Welcome Back' : 'Join Alcruiter'}
              </h1>
              <p className="text-gray-500 text-sm font-medium">
                {isLogin 
                  ? 'Elevate your interview performance with AI.' 
                  : 'Start your journey to tech excellence.'}
              </p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              {!isLogin && (
                <div className="group">
                  <label className="block mb-2 text-xs font-black text-gray-500 uppercase tracking-widest group-focus-within:text-indigo-400 transition-colors">
                    Full Name
                  </label>
                  <input
                    type="text"
                    className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-2xl p-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder-gray-600 backdrop-blur-sm"
                    placeholder="e.g. Aishani Billore"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>
              )}

              <div className="group">
                <label className="block mb-2 text-xs font-black text-gray-500 uppercase tracking-widest group-focus-within:text-indigo-400 transition-colors">
                  Email Address
                </label>
                <input
                  type="email"
                  className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-2xl p-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder-gray-600 backdrop-blur-sm"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="group">
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-xs font-black text-gray-500 uppercase tracking-widest group-focus-within:text-indigo-400 transition-colors">
                    Security Key
                  </label>
                </div>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-2xl p-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder-gray-600 backdrop-blur-sm"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {error && (
                <div className="p-4 bg-red-900/20 border border-red-500/40 rounded-2xl text-red-400 text-xs font-bold animate-shake">
                  ⚠️ {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 text-white font-black text-lg rounded-2xl shadow-xl shadow-indigo-600/20 transition-all active:scale-[0.98] mt-4"
              >
                {isLoading 
                  ? (isLogin ? 'Authenticating...' : 'Creating Profile...') 
                  : (isLogin ? 'Sign In Now' : 'Create AI Account')}
              </button>

              <div className="text-center pt-4 border-t border-gray-800/50">
                <button
                  type="button"
                  onClick={() => { setIsLogin(!isLogin); setError(''); }}
                  className="text-indigo-400 font-black hover:text-indigo-300 transition-colors text-xs uppercase tracking-widest"
                >
                  {isLogin 
                    ? "New to Alcruiter? Sign Up →" 
                    : "Already Have Access? Sign In →"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Login;