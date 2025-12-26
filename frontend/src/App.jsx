import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Placeholder components
const Home = () => (
  <div style={{ textAlign: 'center', marginTop: '50px' }}>
    <h1>Welcome to Document Analysis Platform</h1>
    <p>Please Login to continue.</p>
    <Link to="/login">Login</Link>
  </div>
);

const Login = () => <h2>Login Page (TODO)</h2>;
const Dashboard = () => <h2>Dashboard (TODO)</h2>;

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

