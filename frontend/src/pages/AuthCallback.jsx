import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AuthCallback() {
  const navigate = useNavigate();

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
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
      navigate("/", { replace: true });
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