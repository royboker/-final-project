import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import Login    from "./pages/Login";
import Register from "./pages/Register";
import AuthCallback from "./pages/AuthCallback";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={<LandingPage />} />
<Route path="/login"    element={<Login />} />
<Route path="/register" element={<Register />} /> 
      </Routes>
    </BrowserRouter>
  );
}