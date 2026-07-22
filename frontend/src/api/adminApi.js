import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

/*
Attach JWT token automatically
*/
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("token");

  if (token) {
    req.headers.Authorization = `Bearer ${token}`;
  }

  return req;
});


/* ==============================
   AUTH API
============================== */

export const loginUser = (employeeId, password) => {
  const formData = new URLSearchParams();

  formData.append("username", employeeId);
  formData.append("password", password);

  return API.post("/api/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
};


/* ==============================
   ANALYTICS API
============================== */

export const getDailyAttendance = () =>
  API.get("/api/analytics/daily");

export const getSpoofSummary = () =>
  API.get("/api/analytics/spoof-summary");

export const getSuccessRate = () =>
  API.get("/api/analytics/success-rate");

export const getLateReport = () =>
  API.get("/api/analytics/late-report");

export const getEmployeeHistory = (employeeId) =>
  API.get(`/api/analytics/employee/${employeeId}`);


/* ==============================
   ATTENDANCE API
============================== */

export const markAttendance = (image_base64, device = "WEB_CAM") =>
  API.post("/api/attendance/mark", {
    image_base64,
    device,
  });


/* ==============================
   ATTENDANCE LOGS
============================== */

export const fetchAttendanceLogs = () =>
  API.get("/api/attendance/records");

export const fetchAttendanceLogsByDate = (
  startDate,
  endDate,
  employeeId = ""
) =>
  API.get("/api/attendance/records", {
    params: {
      start_date: startDate,
      end_date: endDate,
      employee_id: employeeId,
    },
  });


/* ==============================
   EMPLOYEE MANAGEMENT (ADMIN)
============================== */

export const getEmployees = () =>
  API.get("/api/admin/users/");

export const createEmployee = (employee_id, name, password) =>
  API.post("/api/admin/users/", {
    employee_id,
    name,
    password,
    role: "employee",
  });

export const deleteEmployee = (employeeId) =>
  API.delete(`/api/admin/users/${employeeId}`);


/* ==============================
   ADMIN FACE ENROLLMENT
============================== */

export const enrollFace = (employeeId, image_base64) =>
  API.post(`/api/admin/face/enroll/${employeeId}`, {
    image_base64,
  });



  // ==============================
// FACE MANAGEMENT
// ==============================

export const deleteFace = (employeeId) =>
  API.delete(`/api/admin/face/delete/${employeeId}`);

export const updateFace = (employeeId) =>
  `/admin-face?employee=${employeeId}`;