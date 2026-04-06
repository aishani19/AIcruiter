import React, { useState, useEffect, useRef } from 'react';
import Navbar from './Navbar';
import io from 'socket.io-client';
import LoadingSpinner from './LoadingSpinner';

const PeerMatch = () => {
  const [status, setStatus] = useState('Idle');
  const [socket, setSocket] = useState(null);
  const [inCall, setInCall] = useState(false);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const roomRef = useRef(null);

  const iceServers = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
    ],
  };

  useEffect(() => {
    // Determine socket URL - use window.location if on the same host
    const socketUrl = window.location.hostname === 'localhost' ? 'http://localhost:5000' : '/';
    const newSocket = io(socketUrl);
    setSocket(newSocket);

    newSocket.on('waiting', (data) => {
      setStatus(data.message);
    });

    newSocket.on('matched', async (data) => {
      setStatus(`Matched! Connecting...`);
      roomRef.current = data.room;
      await setupWebRTC(newSocket, data.role, data.room);
    });

    newSocket.on('webrtc_offer', async (offer) => {
      if (peerConnectionRef.current) {
        await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(offer));
        const answer = await peerConnectionRef.current.createAnswer();
        await peerConnectionRef.current.setLocalDescription(answer);
        newSocket.emit('webrtc_answer', { room: roomRef.current, answer });
      }
    });

    newSocket.on('webrtc_answer', async (answer) => {
      if (peerConnectionRef.current) {
        await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(answer));
      }
    });

    newSocket.on('webrtc_ice_candidate', async (candidate) => {
      if (peerConnectionRef.current) {
        try {
          await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (e) {
          console.error("Error adding ice candidate", e);
        }
      }
    });

    return () => {
      newSocket.disconnect();
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
      }
    };
  }, []);

  const setupWebRTC = async (sock, role, room) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      localStreamRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
      
      const peerConnection = new RTCPeerConnection(iceServers);
      peerConnectionRef.current = peerConnection;

      stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));

      peerConnection.ontrack = (event) => {
        setInCall(true);
        setStatus("Live Call");
        if (remoteVideoRef.current && remoteVideoRef.current.srcObject !== event.streams[0]) {
          remoteVideoRef.current.srcObject = event.streams[0];
        }
      };

      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          sock.emit('webrtc_ice_candidate', { room, candidate: event.candidate });
        }
      };

      if (role === 'caller') {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        sock.emit('webrtc_offer', { room, offer });
      }
    } catch (err) {
      console.error("Error accessing media devices.", err);
      setStatus("Error accessing camera/microphone.");
    }
  };

  const handleFindPeer = () => {
    if (socket) {
      setStatus("Entering Queue...");
      socket.emit('join_queue', {});
    }
  };

  const handleHangup = () => {
    window.location.reload(); 
  };

  return (
    <div className="bg-gradient-to-b from-black via-gray-900 to-purple-900 min-h-screen text-white pt-24 font-sans flex flex-col">
      <Navbar />
      <div className="flex-grow container mx-auto px-6 max-w-6xl pb-20">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-500 mb-4 inline-block tracking-tight">
             Peer Live Interviews
          </h1>
          <p className="text-gray-400 text-lg font-medium">Practice with a shadow candidate in real-time.</p>
        </div>

        <div className="bg-gray-950/60 backdrop-blur-2xl rounded-3xl border border-gray-800 shadow-2xl p-8 md:p-12">
          <div className="flex items-center justify-between mb-10">
             <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${status === 'Idle' ? 'bg-gray-500' : 'bg-green-500 animate-pulse'}`}></div>
                <span className="text-xs uppercase font-black tracking-widest text-gray-500">System Status: <span className="text-white">{status}</span></span>
             </div>
             {inCall && <div className="text-xs font-black text-red-500 animate-pulse tracking-widest uppercase">Recording Live</div>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            <div className="relative group">
              <h3 className="text-sm font-black text-indigo-400 uppercase tracking-widest mb-4">Your Feed</h3>
              <div className="aspect-video bg-black rounded-2xl overflow-hidden border-2 border-indigo-500/20 shadow-2xl group-hover:border-indigo-500/40 transition-all">
                <video ref={localVideoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                {(!localStreamRef.current && status === 'Idle') && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/50 backdrop-blur-sm">
                     <span className="text-gray-600 text-6xl">🔒</span>
                     <span className="text-gray-500 text-xs font-bold mt-4 uppercase tracking-tighter">Your camera is off</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="relative group">
              <h3 className="text-sm font-black text-pink-500 uppercase tracking-widest mb-4">Peer Stream</h3>
              <div className="aspect-video bg-black rounded-2xl overflow-hidden border-2 border-pink-500/20 shadow-2xl group-hover:border-pink-500/40 transition-all">
                <video ref={remoteVideoRef} autoPlay playsInline className="w-full h-full object-cover" />
                {!inCall && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/50 backdrop-blur-sm">
                    {status.includes('Queue') || status.includes('Waiting') ? (
                      <>
                        <div className="mb-4"><LoadingSpinner /></div>
                        <span className="text-indigo-400 text-xs font-black uppercase tracking-widest">Searching the globe...</span>
                      </>
                    ) : (
                      <>
                        <span className="text-gray-600 text-6xl">👥</span>
                        <span className="text-gray-500 text-xs font-bold mt-4 uppercase tracking-tighter">Waiting for match</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mt-12 flex flex-col items-center gap-6">
            {!inCall && status === 'Idle' ? (
              <button
                onClick={handleFindPeer}
                className="group relative bg-indigo-600 hover:bg-indigo-500 text-white font-black text-xl py-6 px-16 rounded-3xl shadow-2xl shadow-indigo-600/30 transition-all transform hover:scale-105 active:scale-95"
              >
                <span className="relative z-10 flex items-center gap-3">
                  Match with a Peer <span className="opacity-50 group-hover:translate-x-1 transition-transform">→</span>
                </span>
                <div className="absolute inset-0 bg-white/20 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </button>
            ) : inCall ? (
              <button
                onClick={handleHangup}
                className="bg-red-600 hover:bg-red-700 text-white font-black text-xl py-6 px-16 rounded-3xl shadow-2xl shadow-red-600/30 transition-all transform hover:scale-105 active:scale-95"
              >
                End Mock Session
              </button>
            ) : (
               <button
                 disabled
                 className="bg-gray-800 text-gray-500 font-black text-xl py-6 px-16 rounded-3xl opacity-50 cursor-not-allowed"
               >
                 In Queue...
               </button>
            )}
            <p className="text-gray-500 text-xs font-bold uppercase tracking-widest">Global matchmaking is active. Peers are online.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PeerMatch;
