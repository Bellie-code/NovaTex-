const BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";


export async function login(employee_id, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: employee_id,
      password: password,
    }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  return data;
}

export async function recognizeFace(token, image_base64) {
  const res = await fetch(`${BASE_URL}/recognition/recognize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ image_base64 }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Recognition failed");
  return data;
}

export async function markAttendance(token, image_base64) {
  const res = await fetch(`${BASE_URL}/attendance/mark`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ image_base64 }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Attendance failed");
  return data;
}

export async function getAttendanceHistory(token) {
  const res = await fetch(`${BASE_URL}/attendance/history`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "History fetch failed");
  return data;
}
