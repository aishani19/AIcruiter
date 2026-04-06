import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Lazy load all route components — this defers module evaluation and
// prevents one bad import from crashing the entire app on startup
const AboutPage     = React.lazy(() => import('./components/AboutPage'));
const GetStarted    = React.lazy(() => import('./components/GetStarted'));
const Practice      = React.lazy(() => import('./components/Practice'));
const Feedback      = React.lazy(() => import('./components/Feedback'));
const Login         = React.lazy(() => import('./components/Login'));
const Dashboard     = React.lazy(() => import('./components/Dashboard'));
const Leaderboard   = React.lazy(() => import('./components/Leaderboard'));
const PeerMatch     = React.lazy(() => import('./components/PeerMatch'));
const History       = React.lazy(() => import('./components/History'));
const SessionDetail = React.lazy(() => import('./components/SessionDetail'));

// Fallback shown while a lazy component loads
const PageLoader = () => (
  <div style={{
    minHeight: '100vh',
    background: '#000',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    gap: '16px',
    fontFamily: 'sans-serif',
  }}>
    <div style={{
      width: '48px', height: '48px',
      border: '4px solid #4f46e5',
      borderTopColor: 'transparent',
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
    }} />
    <p style={{ color: '#6b7280', fontSize: '14px', letterSpacing: '2px', textTransform: 'uppercase' }}>
      Loading…
    </p>
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

// Error boundary catches any render-time crash per route
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '40px', color: 'white', background: '#0f0221',
          minHeight: '100vh', fontFamily: 'monospace',
        }}>
          <h1 style={{ color: '#f87171', marginBottom: '24px' }}>⚠️ Component Error</h1>
          <pre style={{
            background: '#1e0533', padding: '20px', borderRadius: '12px',
            overflow: 'auto', fontSize: '13px', lineHeight: '1.6',
          }}>
            {this.state.error?.toString()}
            {'\n\n'}
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              marginTop: '24px', padding: '12px 24px',
              background: '#4f46e5', color: 'white',
              border: 'none', borderRadius: '8px', cursor: 'pointer',
            }}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/"                element={<AboutPage />} />
            <Route path="/login"           element={<Login />} />
            <Route path="/get-started"     element={<GetStarted />} />
            <Route path="/practice"        element={<Practice />} />
            <Route path="/feedback"        element={<Feedback />} />
            <Route path="/dashboard"       element={<Dashboard />} />
            <Route path="/leaderboard"     element={<Leaderboard />} />
            <Route path="/peer-match"      element={<PeerMatch />} />
            <Route path="/history"         element={<History />} />
            <Route path="/history/:sessionId" element={<SessionDetail />} />
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  );
};

export default App;