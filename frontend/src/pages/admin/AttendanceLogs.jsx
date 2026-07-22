import { useState } from "react";
import { fetchAttendanceLogsByDate } from "../../api/adminApi";

export default function AttendanceLogs() {

  const [logs, setLogs] = useState([]);

  const [startDate, setStartDate] = useState("2026-01-01T00:00:00");
  const [endDate, setEndDate] = useState("2026-12-31T23:59:59");

  const [employeeId, setEmployeeId] = useState("");

  const loadLogs = async () => {

    try {

      const res = await fetchAttendanceLogsByDate(
        startDate,
        endDate,
        employeeId
      );

      setLogs(res.data);

    } catch (err) {

      console.error("Logs Error:", err);

    }

  };

  return (

    <div className="min-h-screen bg-gradient-to-br from-[#0B0E14] via-[#14103A] to-[#2B1450] p-10 text-white">

      <h1 className="text-4xl font-bold mb-8">
        Attendance Logs
      </h1>

      {/* Filters */}

      <div className="flex gap-4 mb-8">

        <input
          type="datetime-local"
          className="px-4 py-3 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-xl text-white outline-none"
          value={startDate.replace("T00:00:00", "T00:00")}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <input
          type="datetime-local"
          className="px-4 py-3 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-xl text-white outline-none"
          value={endDate.replace("T23:59:59", "T23:59")}
          onChange={(e) => setEndDate(e.target.value)}
        />

        {/* Employee Search */}

        <input
          type="text"
          placeholder="Search Employee ID"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          className="px-4 py-3 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-xl text-white outline-none placeholder-gray-400"
        />

        <button
          onClick={loadLogs}
          className="px-6 py-3 rounded-2xl font-semibold bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 hover:opacity-90 transition shadow-lg"
        >
          Load Logs
        </button>

      </div>

      {/* Table */}

      <div className="bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl shadow-xl overflow-auto">

        <table className="w-full text-left">

          <thead className="border-b border-white/10">

            <tr className="text-gray-300">

              <th className="p-4">Employee ID</th>

              <th className="p-4">Employee Name</th>

              <th className="p-4">Date</th>

              <th className="p-4">Time</th>

              <th className="p-4">Status</th>

              <th className="p-4">Spoof</th>

              <th className="p-4">Confidence</th>

              <th className="p-4">Device</th>

            </tr>

          </thead>

          <tbody>

            {logs.map((log) => (

              <tr
                key={log.id}
                className="border-b border-white/10 hover:bg-white/5 transition"
              >

                <td className="p-4">
                  {log.employee_id || "--"}
                </td>

                <td className="p-4">
                  {log.name || "--"}
                </td>

                <td className="p-4">
                  {new Date(log.timestamp).toLocaleDateString()}
                </td>

                <td className="p-4">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>

                <td className="p-4">

                  <span
                    className={
                      log.status === "SUCCESS"
                        ? "text-green-400 font-semibold"
                        : "text-red-400 font-semibold"
                    }
                  >
                    {log.status}
                  </span>

                </td>

                <td className="p-4">

                  {log.spoof_status === "REAL" ? (

                    <span className="text-green-400">
                      REAL
                    </span>

                  ) : (

                    <span className="text-red-400">
                      SPOOF
                    </span>

                  )}

                </td>

                <td className="p-4">
                  {(Number(log.confidence) * 100).toFixed(2)}%
                </td>

                <td className="p-4 text-gray-300">
                  {log.device}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );

}