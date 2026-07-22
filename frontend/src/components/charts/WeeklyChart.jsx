import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

export default function WeeklyChart({ weeklyStats }) {
  const labels = weeklyStats.map((item) => item.date);
  const values = weeklyStats.map((item) => item.count);

  const data = {
    labels,
    datasets: [
      {
        label: "Weekly Attendance",
        data: values,
        borderWidth: 2,
        fill: false,
      },
    ],
  };

  return <Line data={data} />;
}
