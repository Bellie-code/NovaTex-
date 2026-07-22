import React, { useEffect, useState } from "react";
import {
  getEmployees,
  createEmployee,
  deleteEmployee,
  deleteFace,
} from "../../api/adminApi";

import { useNavigate } from "react-router-dom";

export default function EmployeeManagement() {
  const [employeeId, setEmployeeId] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [users, setUsers] = useState([]);

  const navigate = useNavigate();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const res = await getEmployees();
      setUsers(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  const handleCreateEmployee = async () => {
    try {
      await createEmployee(employeeId, name, password);

      setEmployeeId("");
      setName("");
      setPassword("");

      loadUsers();
    } catch (err) {
      console.log(err);
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    try {
      await deleteEmployee(employeeId);
      loadUsers();
    } catch (err) {
      console.log(err);
    }
  };

  const handleDeleteFace = async (employeeId) => {
    try {
      await deleteFace(employeeId);
      loadUsers();
    } catch (err) {
      console.log(err);
    }
  };

  const handleEnrollFace = (employeeId) => {
    navigate(`/admin-face?employee=${employeeId}`);
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-[#0B0E14] via-[#14103A] to-[#2B1450]">
      <div className="flex-1 p-10 text-white">

        {/* CREATE EMPLOYEE CARD */}
        <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-xl mb-10">

          <div className="grid grid-cols-4 gap-6">

            <input
              type="text"
              placeholder="Employee ID"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-white outline-none placeholder-gray-400"
            />

            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-white outline-none placeholder-gray-400"
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-white outline-none placeholder-gray-400"
            />

            <button
              onClick={handleCreateEmployee}
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl px-6 py-3 font-semibold hover:opacity-90 transition"
            >
              Create
            </button>

          </div>

        </div>

        {/* EMPLOYEE TABLE */}
        <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-xl">

          <table className="w-full text-gray-200">

            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3">Employee ID</th>
                <th className="text-left">Name</th>
                <th className="text-left">Role</th>
                <th className="text-left">Face Status</th>
                <th className="text-left">Last Updated</th>
                <th className="text-left">Action</th>
              </tr>
            </thead>

            <tbody>

              {users.map((user) => (

                <tr
                  key={user.employee_id}
                  className="border-b border-white/10"
                >

                  <td className="py-4">{user.employee_id}</td>

                  <td>{user.name}</td>

                  <td>{user.role}</td>

                  <td>
                    {user.face_enrolled ? (
                      <span className="text-green-400 font-semibold">
                        🟢 Enrolled
                      </span>
                    ) : (
                      <span className="text-red-400 font-semibold">
                        🔴 Not Enrolled
                      </span>
                    )}
                  </td>

                  <td>
                    {user.face_updated_at
                      ? new Date(user.face_updated_at).toLocaleString()
                      : "--"}
                  </td>

                  <td>

                    <div className="flex flex-wrap gap-2">

                      {!user.face_enrolled ? (

                        <button
                          onClick={() => handleEnrollFace(user.employee_id)}
                          className="px-3 py-2 rounded-lg bg-blue-500/30 text-blue-300 hover:bg-blue-500/50 transition text-sm"
                        >
                          Enroll
                        </button>

                      ) : (

                        <>
                          <button
                            onClick={() => handleEnrollFace(user.employee_id)}
                            className="px-3 py-2 rounded-lg bg-yellow-500/30 text-yellow-300 hover:bg-yellow-500/50 transition text-sm"
                          >
                            Update Face
                          </button>

                          <button
                            onClick={() => handleDeleteFace(user.employee_id)}
                            className="px-3 py-2 rounded-lg bg-purple-500/30 text-purple-300 hover:bg-purple-500/50 transition text-sm"
                          >
                            Delete Face
                          </button>
                        </>

                      )}

                      <button
                        onClick={() =>
                          handleDeleteEmployee(user.employee_id)
                        }
                        className="px-3 py-2 rounded-lg bg-red-500/30 text-red-300 hover:bg-red-500/50 transition text-sm"
                      >
                        Delete
                      </button>

                    </div>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>
    </div>
  );
}