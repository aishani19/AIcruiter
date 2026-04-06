import React, { useState, useEffect } from 'react';

const LoadingSpinner = () => {
  const sentences = [
    'Converting video to audio...',
    'Transcribing audio using GenAI...',
    'Getting average confidence score from Google Cloud Speech-to-Text...',
    'Performing sentiment analysis...',
    'Calculating average sentence length...',
    'Detecting filler words...',
    'Calculating response duration...',
    'Calculating eye contact percentage...',
  ];

  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Update the current sentence periodically
    const sentenceInterval = setInterval(() => {
      setCurrentSentenceIndex((prevIndex) => (prevIndex + 1) % sentences.length);
    }, 1500); // Change the sentence every 1.5 seconds

    // Increment progress for the loading bar
    const progressInterval = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= 100) {
          clearInterval(progressInterval); // Stop progress at 100%
          return 100;
        }
        return prevProgress + 5; // Increment progress by 5%
      });
    }, 300); // Update progress every 200ms

    return () => {
      clearInterval(sentenceInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="text-white text-xl font-semibold mb-4">
        {sentences[currentSentenceIndex]}
      </div>
      <div className="w-64 h-2 bg-gray-700 rounded-full overflow-hidden mb-2">
        <div
          className="h-full bg-blue-500 transition-all duration-200"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="text-white text-sm">{progress}%</div>
    </div>
  );
};

export default LoadingSpinner;