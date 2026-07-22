import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function MonthlyChart({ monthlyStats }) {
  const labels = monthlyStats.map((item) => item.month);
  const values = monthlyStats.map((item) => item.count);

  const data = {
    labels,
    datasets: [
      {
        label: "Monthly Attendance",
        data: values,
        borderWidth: 1,
      },
    ],
  };

  return <Bar data={data} />;
}
