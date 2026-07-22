import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function AnalyticsCharts() {
  const data = [
    { day: "Mon", attendance: 30 },
    { day: "Tue", attendance: 42 },
    { day: "Wed", attendance: 35 },
    { day: "Thu", attendance: 50 },
    { day: "Fri", attendance: 47 },
    { day: "Sat", attendance: 60 },
    { day: "Sun", attendance: 40 },
  ];

  return (
    <div className="rounded-3xl bg-white/50 border border-white/40 shadow-2xl backdrop-blur-xl p-6">
      <h2 className="text-xl font-extrabold text-gray-900 mb-4">
        📈 Weekly Attendance Analytics
      </h2>

      <p className="text-gray-700 font-medium mb-5">
        This chart shows total attendance count per day.
      </p>

      <div className="w-full h-[260px]">
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="4 4" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="attendance" strokeWidth={4} dot={{ r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
