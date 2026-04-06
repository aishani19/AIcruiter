import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "./LoadingSpinner";
import api from "../utils/api";

const GetStarted = () => {
  const [resume, setResume] = useState(null);
  const [occupation, setOccupation] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [seniorityLevel, setSeniorityLevel] = useState("fresher");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  // 🔐 Redirect if not logged in
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setResume(file);
      setError("");
    } else {
      setError("Only PDF files are allowed.");
    }
  };

  const validateForm = () => {
    if (!resume) return "Please upload your resume.";
    if (!occupation.trim()) return "Occupation is required.";
    if (numQuestions < 1 || numQuestions > 20) return "Questions must be 1-20.";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("occupation", occupation);
      formData.append("num_questions", numQuestions);
      formData.append("seniority_level", seniorityLevel);

      // Using the api.js instance (Axios)
      const response = await api.post("/generate-questions", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const data = response.data;
      
      // ✅ Redirect to practice page with questions
      navigate("/practice", {
        state: { 
          questions: data.questions,
          sessionId: data.session_id,
          seniorityLevel: seniorityLevel
        },
      });

    } catch (err) {
      console.error("❌ ERROR:", err);
      setError(err.response?.data?.error || "Failed to generate questions. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-t from-black via-purple-900 to-gray-900 text-white flex items-center justify-center p-4">
      {isLoading && <LoadingSpinner />}

      <div className="bg-gray-900/60 backdrop-blur-xl p-10 rounded-3xl shadow-2xl max-w-lg w-full border border-gray-800">
        <h1 className="text-4xl font-black text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
          Launch Interview
        </h1>

        {error && (
          <div className="bg-red-900/20 border border-red-500/40 p-4 rounded-xl text-red-400 text-sm mb-6 text-center">
             ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Resume (PDF Only)</label>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange} 
              className="w-full bg-gray-800 p-3 rounded-xl border border-gray-700 text-sm"
              required
            />
            {resume && <p className="text-xs text-indigo-400 mt-2">✓ {resume.name}</p>}
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Target Occupation</label>
            <input
              type="text"
              placeholder="e.g., Software Engineer"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              className="w-full p-4 bg-gray-800 border border-gray-700 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Experience Level</label>
              <select
                value={seniorityLevel}
                onChange={(e) => setSeniorityLevel(e.target.value)}
                className="w-full p-4 bg-gray-800 border border-gray-700 rounded-2xl outline-none"
              >
                <option value="fresher">Fresher</option>
                <option value="junior">Junior (1-3y)</option>
                <option value="mid">Mid (3-7y)</option>
                <option value="senior">Senior (7y+)</option>
                <option value="lead">Lead/Arch</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Question Count</label>
              <input
                type="number"
                value={numQuestions}
                min="1"
                max="20"
                onChange={(e) => setNumQuestions(Number(e.target.value))}
                className="w-full p-4 bg-gray-800 border border-gray-700 rounded-2xl outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-2xl font-black text-lg shadow-xl shadow-indigo-600/20 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {isLoading ? "Analyzing Resume & Preparing..." : "Start Practice Session"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default GetStarted;