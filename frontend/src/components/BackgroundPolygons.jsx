import React from 'react';

const BackgroundPolygons = () => {
  return (
    <>
      {/* Enlarged Decorative Background Elements */}
      <div
        aria-hidden="true"
        className="absolute inset-x-0 -top-60 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-120"
      >
        <div
          style={{
            clipPath:
              'polygon(60% 30%, 100% 70%, 95% 10%, 80% 0%, 70% 5%, 60% 30%, 50% 60%, 40% 65%, 35% 55%, 30% 35%, 15% 80%, 0% 70%, 20% 100%, 30% 80%, 80% 100%, 60% 30%)',
          }}
          className="relative left-[calc(50%-15rem)] aspect-[1200/700] w-[50rem] -translate-x-1/2 rotate-[25deg] bg-gradient-to-tr from-black to-black opacity-70 sm:left-[calc(50%-40rem)] sm:w-[90rem]"
        />
      </div>
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-[calc(100%-20rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-40rem)]"
      >
      </div>
    </>
  );
};

export default BackgroundPolygons;