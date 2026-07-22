import React from "react";
import { LayoutDashboard, Camera, UserCheck, Users, LogOut, ClipboardList } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function Sidebar({ activePage, setActivePage }) {
console.log("ROLE:", localStorage.getItem("role"));
  const navigate = useNavigate();

  const role = localStorage.getItem("role");

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={20} />, path: "/dashboard" },
    { id: "attendance", label: "Mark Attendance", icon: <UserCheck size={20} />, path: "/attendance" },

    ...(role === "admin"
      ? [
          { id: "face", label: "Face Enrollment", icon: <Camera size={20} />, path: "/enroll" },
          { id: "attendance-logs", label: "Attendance Logs", icon: <ClipboardList size={20} />, path: "/attendance-logs" },
          { id: "employees", label: "Employees", icon: <Users size={20} />, path: "/employees" }
        ]
      : [])
  ];

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.reload();
  };

  return (
    <aside className="w-72 min-h-screen bg-white/5 backdrop-blur-2xl border-r border-white/10 shadow-2xl p-8 relative overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-[-80px] left-[-80px] w-60 h-60 bg-purple-500/30 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-80px] right-[-80px] w-60 h-60 bg-pink-500/30 blur-[120px] rounded-full"></div>

      {/* Logo */}
      <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent relative z-10">
        AI Attendance
      </h1>

      <p className="mt-2 text-sm text-white/60 relative z-10">
        Privacy-Aware Face System
      </p>

      {/* Menu */}
      <div className="mt-12 flex flex-col gap-4 relative z-10">
        {menuItems.map((item) => {

          const isActive = activePage === item.id;

          return (
            <motion.button
              key={item.id}
              onClick={() => {
                setActivePage(item.id);
                navigate(item.path);
              }}
              whileHover={{ scale: 1.04, x: 6 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 250, damping: 18 }}
              className={`relative flex items-center gap-4 px-5 py-4 rounded-2xl font-semibold text-white overflow-hidden group
                ${
                  isActive
                    ? "bg-gradient-to-r from-purple-500/40 via-pink-500/30 to-indigo-500/30 shadow-xl"
                    : "bg-white/5 hover:bg-white/10"
                }`}
            >

              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute left-0 top-0 h-full w-1.5 bg-gradient-to-b from-purple-400 to-pink-400 rounded-r-full"
                />
              )}

              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition duration-300 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-indigo-500/10 blur-xl"></div>

              <motion.span
                whileHover={{ rotate: 5 }}
                transition={{ type: "spring", stiffness: 200 }}
                className={`relative z-10 ${
                  isActive
                    ? "text-pink-300"
                    : "text-white/70 group-hover:text-pink-300"
                }`}
              >
                {item.icon}
              </motion.span>

              <span className="relative z-10 tracking-wide">
                {item.label}
              </span>

            </motion.button>
          );
        })}
      </div>

      {/* Logout */}
      <motion.button
        onClick={logout}
        whileHover={{ scale: 1.04, x: 6 }}
        whileTap={{ scale: 0.97 }}
        transition={{ type: "spring", stiffness: 250, damping: 18 }}
        className="mt-16 flex items-center gap-3 px-5 py-4 rounded-2xl bg-red-500/15 hover:bg-red-500/25 text-red-300 transition-all duration-300 w-full relative z-10 shadow-lg"
      >
        <LogOut size={20} />
        Logout
      </motion.button>

    </aside>
  );
}