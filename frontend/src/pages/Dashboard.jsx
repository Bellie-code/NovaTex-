import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, Search } from "lucide-react";
import { motion } from "framer-motion";

import Sidebar from "../components/Sidebar";

import {
  getDailyAttendance,
  getSpoofSummary,
  getSuccessRate
} from "../api/adminApi";

export default function Dashboard({ token, setToken }) {

  const navigate = useNavigate();

  const [activePage, setActivePage] = useState("dashboard");

  const [todayAttendance, setTodayAttendance] = useState(0);
  const [spoofAttempts, setSpoofAttempts] = useState(0);
  const [recognizedEmployees, setRecognizedEmployees] = useState(0);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setToken(null);
    navigate("/");
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {

      const daily = await getDailyAttendance();
      const spoof = await getSpoofSummary();
      const success = await getSuccessRate();

      const today = new Date().toISOString().slice(0, 10);

      const todayData = daily.data.find(d => d.date === today);

      if (todayData) {
        setTodayAttendance(todayData.count);
      }

      setSpoofAttempts(spoof.data.SPOOF || 0);

      setRecognizedEmployees(success.data.success_count || 0);

    } catch (err) {
      console.log("Analytics error:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 25 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen flex bg-gradient-to-br from-[#0B0E14] via-[#14103A] to-[#2B1450]"
    >

      {/* Sidebar (Using Component Now) */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content */}
      <div className="flex-1 p-10">

        {/* Top Bar */}
        <div className="flex justify-between items-center mb-12">

          <div>
            <h2 className="text-4xl font-bold text-white mb-3">
              Welcome Back 👋
            </h2>
            <p className="text-gray-300">
              Monitor attendance, spoof detection & recognition analytics.
            </p>
          </div>

          <div className="flex items-center gap-5">

            <div className="flex items-center bg-white/10 border border-white/10 backdrop-blur-xl px-4 py-2 rounded-2xl w-[280px] shadow-lg">
              <Search size={18} className="text-white/60" />
              <input
                type="text"
                placeholder="Search..."
                className="bg-transparent outline-none text-white placeholder-white/50 px-3 w-full"
              />
            </div>

            <button className="w-12 h-12 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center hover:bg-white/20 transition-all duration-300 shadow-lg">
              <Bell className="text-white/70" size={20} />
            </button>

            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 shadow-xl border border-white/20"></div>

          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6">

          <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:scale-[1.02] transition-all duration-300">
            <h3 className="text-gray-200 text-sm">Today's Attendance</h3>
            <p className="text-4xl font-bold text-white mt-3">{todayAttendance}</p>
            <p className="text-green-400 text-sm mt-2">AI Verified</p>
          </div>

          <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:scale-[1.02] transition-all duration-300">
            <h3 className="text-gray-200 text-sm">Spoof Attempts</h3>
            <p className="text-4xl font-bold text-white mt-3">{spoofAttempts}</p>
            <p className="text-red-400 text-sm mt-2">Blocked successfully</p>
          </div>

          <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:scale-[1.02] transition-all duration-300">
            <h3 className="text-gray-200 text-sm">Recognized Employees</h3>
            <p className="text-4xl font-bold text-white mt-3">{recognizedEmployees}</p>
            <p className="text-purple-300 text-sm mt-2">AI Verified</p>
          </div>

        </div>

        {/* Banner */}
        <div className="mt-12 bg-gradient-to-r from-purple-500/30 via-pink-500/20 to-indigo-500/20 rounded-3xl p-10 border border-white/10 shadow-2xl hover:scale-[1.01] transition-all duration-300">

          <h3 className="text-2xl font-bold text-white mb-2">
            Next-Gen AI Attendance
          </h3>

          <p className="text-gray-200">
            Face Recognition + Anti-Spoof Detection + Secure JWT Authentication.
          </p>

        </div>

      </div>
    </motion.div>
  );
}