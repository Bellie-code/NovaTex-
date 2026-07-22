import React from "react";
import { Bell, Search } from "lucide-react";

export default function Topbar() {
  return (
    <header className="flex justify-between items-center px-10 py-6 bg-gradient-to-r from-purple-600/20 via-pink-500/10 to-indigo-600/20 border-b border-white/10 backdrop-blur-xl">

      <div>
        <h2 className="text-xl font-bold tracking-tight">
          Welcome Back 👋
        </h2>
        <p className="text-sm text-white/60">
          Monitor attendance & recognition analytics
        </p>
      </div>

      <div className="flex items-center gap-6">

        {/* Search Box */}
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-xl shadow-lg">
          <Search size={18} className="text-white/70" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent outline-none text-sm text-white placeholder-white/50"
          />
        </div>

        {/* Notification */}
        <button className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/10 shadow-lg transition-all duration-300">
          <Bell size={20} />
        </button>

        {/* Avatar */}
        <div className="w-11 h-11 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 shadow-xl border border-white/10"></div>
      </div>
    </header>
  );
}
