import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setSession } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const user = {
      id: params.get("id"),
      name: params.get("name"),
      email: params.get("email"),
      role: params.get("role"),
    };

if (token) {
  setSession(token, user);
  setTimeout(() => navigate("/", { replace: true }), 100);
} else {
  navigate("/login", { replace: true });
}
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", background: "#09090f", color: "#a3e635", fontFamily: "DM Sans" }}>
      Signing you in...
    </div>
  );
}