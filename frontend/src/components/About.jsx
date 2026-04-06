const About = () => {
  return (
    <div className="space-y-12 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Introduction Section */}
      <section className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-2xl shadow-lg p-8 text-center">
        <h2 className="text-4xl font-extrabold text-white mb-4">What We Offer</h2>
        <p className="text-lg text-white leading-relaxed">
          Alcruiter is an advanced platform that leverages artificial intelligence to help you master your interview skills. Through personalized practice sessions and real-time feedback, we prepare you for success in your next interview.
        </p>
      </section>

      {/* Features Section */}
      <section className="grid md:grid-cols-3 gap-8">
        {/* Feature 1 */}
        <div className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-xl p-8 shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform duration-300">
          <h3 className="text-2xl font-bold text-white mb-4">📅 Practice Anytime</h3>
          <p className="text-gray-400 leading-relaxed">
            Access our AI-powered interview practice platform 24/7. Get unlimited attempts to perfect your responses and build your confidence.
          </p>
        </div>

        {/* Feature 2 */}
        <div className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-xl p-8 shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform duration-300">
          <h3 className="text-2xl font-bold text-white mb-4">🧠 Smart Feedback</h3>
          <p className="text-gray-400 leading-relaxed">
            Receive instant, detailed analysis on your responses including tone, pacing, and content relevance to continuously improve.
          </p>
        </div>

        {/* Feature 3 */}
        <div className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-xl p-8 shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform duration-300">
          <h3 className="text-2xl font-bold text-white mb-4">📊 Industry Focus</h3>
          <p className="text-gray-400 leading-relaxed">
            Get questions tailored to your industry and role, ensuring relevant practice that aligns with your career path.
          </p>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-xl p-10 shadow-lg">
        <h2 className="text-5xl font-extrabold text-white text-center mb-8">💡 How It Works</h2>
        <div className="space-y-6 text-gray-300 text-lg">
          <div className="flex items-center gap-4">
            <span className="bg-indigo-600 text-white font-bold rounded-full h-12 w-12 flex items-center justify-center">
              1
            </span>
            <p>Upload your resume to get personalized interview questions tailored to your experience.</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="bg-indigo-600 text-white font-bold rounded-full h-12 w-12 flex items-center justify-center">
              2
            </span>
            <p>Practice answering questions through text or voice recordings in a realistic interview environment.</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="bg-indigo-600 text-white font-bold rounded-full h-12 w-12 flex items-center justify-center">
              3
            </span>
            <p>Receive detailed AI-powered feedback on your tone, clarity, and response quality to improve.</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="bg-indigo-600 text-white font-bold rounded-full h-12 w-12 flex items-center justify-center">
              4
            </span>
            <p>Track your progress over time and become fully prepared for your next big interview!</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;