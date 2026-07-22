import { useRef, useState, useEffect } from "react";

export default function FaceEnroll({ token }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [employeeId, setEmployeeId] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.log(err);
      setMsg(" Camera permission denied!");
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
  };

  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg");
  };

  const enrollFace = async () => {
    setLoading(true);
    setMsg(" Enrolling face...");

    try {
      const imageBase64 = captureFrame();

      const res = await fetch("http://127.0.0.1:8000/api/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          employee_id: employeeId,
          name: name,
          password: password,
          image_base64: imageBase64,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMsg("❌ " + (data.detail || "Enrollment failed!"));
        setLoading(false);
        return;
      }

      setMsg(`✅ Face enrolled successfully for ${data.name}`);
      setLoading(false);
    } catch (err) {
      console.log(err);
      setMsg(" Backend error!");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0E14] via-[#1A1033] to-[#2D124F] p-10">
      <div className="w-full max-w-5xl bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8">

        <h1 className="text-4xl font-bold text-white text-center mb-2">
          Face Enrollment
        </h1>
        <p className="text-gray-300 text-center mb-8">
          Capture a live face image and register employee details.
        </p>

        <div className="grid grid-cols-2 gap-6">

          <div className="rounded-3xl overflow-hidden border border-white/10 shadow-xl">
            <video ref={videoRef} autoPlay className="w-full h-[400px] object-cover" />
          </div>

          <div className="space-y-4">
            <input
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              placeholder="Employee ID (EMP301)"
              className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-purple-400"
            />

            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Employee Name"
              className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-pink-400"
            />

            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              type="password"
              className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-indigo-400"
            />

            <button
              onClick={enrollFace}
              disabled={loading}
              className="w-full py-4 rounded-2xl font-semibold text-white text-lg bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 hover:opacity-90 transition shadow-lg"
            >
              {loading ? "Enrolling..." : "📸 Capture & Enroll Face"}
            </button>

            {msg && (
              <div className="mt-4 text-center text-lg font-semibold text-white">
                {msg}
              </div>
            )}
          </div>
        </div>

        <canvas ref={canvasRef} className="hidden"></canvas>
      </div>
    </div>
  );
}
