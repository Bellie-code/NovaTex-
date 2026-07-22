import { useEffect, useState } from "react";
import { fetchDashboardStats } from "../../api/adminApi";

import WeeklyChart from "../../components/charts/WeeklyChart";
import MonthlyChart from "../../components/charts/MonthlyChart";

import Sidebar from "../../components/Sidebar";
import Attendance from "../Attendance";
import FaceEnroll from "../FaceEnroll";
import AttendanceLogs from "./AttendanceLogs";
import EmployeeManagement from "./EmployeeManagement";

export default function Dashboard() {

  const [stats, setStats] = useState(null);

  // controls sidebar navigation
  const [activePage, setActivePage] = useState("dashboard");

  useEffect(() => {
    fetchDashboardStats()
      .then((res) => setStats(res.data))
      .catch((err) => console.error("Dashboard Error:", err));
  }, []);

  if (!stats) return <p className="text-center mt-10">Loading Dashboard...</p>;

  return (
    <div className="flex">

      {/* Sidebar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Page Content */}
      <div className="flex-1">

        {activePage === "dashboard" && (

          <div className="p-6 bg-gray-100 min-h-screen">

            <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-gray-600">Total Users</h2>
                <p className="text-2xl font-bold">{stats.total_users}</p>
              </div>

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-gray-600">Today Attendance</h2>
                <p className="text-2xl font-bold">{stats.today_attendance}</p>
              </div>

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-gray-600">Spoof Attempts Today</h2>
                <p className="text-2xl font-bold text-red-500">
                  {stats.spoof_attempts_today}
                </p>
              </div>

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-gray-600">Rejected Today</h2>
                <p className="text-2xl font-bold text-orange-500">
                  {stats.rejected_attendance_today}
                </p>
              </div>

            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-xl font-semibold mb-4">
                  Weekly Attendance
                </h2>
                <WeeklyChart weeklyStats={stats.weekly_stats} />
              </div>

              <div className="bg-white p-4 rounded-xl shadow">
                <h2 className="text-xl font-semibold mb-4">
                  Monthly Attendance
                </h2>
                <MonthlyChart monthlyStats={stats.monthly_stats} />
              </div>

            </div>

          </div>

        )}

        {activePage === "attendance" && <Attendance />}

        {activePage === "face" && <FaceEnroll />}

        {activePage === "logs" && <AttendanceLogs />}

        {activePage === "employees" && <EmployeeManagement />}

      </div>

    </div>
  );
}