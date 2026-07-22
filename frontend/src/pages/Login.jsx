import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/adminApi";

export default function Login({ setToken }) {

  const [employeeId, setEmployeeId] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg("Logging in...");

    try {

      const res = await loginUser(employeeId, password);
      console.log("LOGIN RESPONSE:", res.data);

      const token = res.data.access_token;
      const role = res.data.role; // <-- get role from backend

      // store token + role
      localStorage.setItem("token", token);
      localStorage.setItem("role", role);

      setToken(token);

      setMsg("✅ Login successful!");
      setLoading(false);

      setTimeout(() => {
        navigate("/dashboard");
      }, 800);

    } catch (err) {

      console.log(err);

      const errorMsg =
        err?.response?.data?.detail || "Invalid employee ID or password";

      setMsg(`❌ ${errorMsg}`);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0E14] via-[#1A1033] to-[#2D124F] p-6">

      <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">

        <h1 className="text-3xl font-bold text-white mb-2">
          Face Attendance AI
        </h1>

        <p className="text-gray-300 mb-6">
          Secure Login • AI Recognition • Spoof Protection
        </p>

        <form onSubmit={handleLogin} className="space-y-5">

          <div>
            <label className="text-gray-200 text-sm">Employee ID</label>

            <input
              type="text"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="w-full mt-2 px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-pink-400"
              placeholder="EMP201"
              required
            />
          </div>

          <div>
            <label className="text-gray-200 text-sm">Password</label>

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-2 px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-purple-400"
              placeholder="Enter password"
              required
            />
          </div>

          <button
            disabled={loading}
            className="w-full py-3 rounded-2xl font-semibold text-white bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 hover:opacity-90 transition shadow-lg"
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        {msg && (
          <p className="mt-5 text-center text-sm text-gray-200">
            {msg}
          </p>
        )}

        <p className="text-center text-xs text-gray-400 mt-6">
          © 2026 Face Attendance AI • Premium UI System
        </p>

      </div>

    </div>
  );
}