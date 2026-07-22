import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Attendance from "./pages/Attendance";
import FaceEnroll from "./pages/FaceEnroll";
import AttendanceLogs from "./pages/admin/AttendanceLogs";
import EmployeeManagement from "./pages/admin/EmployeeManagement";
import AdminFaceEnroll from "./pages/admin/AdminFaceEnroll";

export default function App() {

  const [token, setToken] = useState(localStorage.getItem("token"));

  return (
    <Router>

      <Routes>

        {/* Login */}
        <Route
          path="/"
          element={
            token
              ? <Navigate to="/dashboard" />
              : <Login setToken={setToken} />
          }
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={
            token
              ? <Dashboard token={token} setToken={setToken} />
              : <Navigate to="/" />
          }
        />

        {/* Attendance */}
        <Route
          path="/attendance"
          element={
            token
              ? <Attendance token={token} />
              : <Navigate to="/" />
          }
        />

        {/* Face Enrollment */}
        <Route
          path="/enroll"
          element={
            token && localStorage.getItem("role") === "admin"
              ? <FaceEnroll token={token} />
              : <Navigate to="/dashboard" />
          }
        />

        {/* Attendance Logs */}
        <Route
          path="/attendance-logs"
          element={
            token
              ? <AttendanceLogs />
              : <Navigate to="/" />
          }
        />

        {/* Employees */}
        <Route
          path="/employees"
          element={
            token
              ? <EmployeeManagement />
              : <Navigate to="/" />
          }
        />

        {/* Admin Face Enroll */}
        <Route
          path="/admin-face"
          element={
            token
              ? <AdminFaceEnroll />
              : <Navigate to="/" />
          }
        />

      </Routes>

    </Router>
  );
}