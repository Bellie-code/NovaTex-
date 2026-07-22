import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

export default function Attendance({ token }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // Start webcam
  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch(() => {
        setMsg("❌ Webcam access denied");
      });

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  // Capture image from webcam
  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!canvas || !video) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg");
  };

  // Mark attendance
  const markAttendance = async () => {
    if (!token) {
      setMsg("❌ Invalid or expired token. Please login again.");
      return;
    }

    setLoading(true);
    setMsg("");

    try {
      const imageBase64 = captureImage();

      const res = await fetch("http://127.0.0.1:8000/api/attendance/mark", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          image_base64: imageBase64,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMsg(`❌ ${data.detail}`);
        setLoading(false);
        return;
      }

      setMsg(`✅ Attendance Marked Successfully for ${data.name}`);
    } catch (err) {
      setMsg("❌ Error connecting to backend!");
    }

    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }} // start hidden + down
      animate={{ opacity: 1, y: 0 }} // fade in + move up
      exit={{ opacity: 0, y: -20 }} // when leaving fade out + move up
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="flex justify-center items-center min-h-screen px-6"
    >
      <div className="w-full max-w-3xl bg-white/10 border border-white/10 backdrop-blur-2xl rounded-[32px] shadow-2xl p-10">
        <h1 className="text-5xl font-extrabold text-center bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
          Mark Attendance
        </h1>

        <p className="text-center text-white/70 mt-3 mb-8">
          Use your live webcam to verify identity and mark attendance.
        </p>

        {/* Webcam */}
        <div className="relative rounded-[28px] overflow-hidden border border-white/10 shadow-xl">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-[360px] object-cover bg-black/50"
          />

          <span className="absolute top-4 right-4 px-4 py-1 rounded-full bg-green-500/20 text-green-300 border border-green-400/30 text-sm font-semibold">
            LIVE
          </span>
        </div>

        {/* Button */}
        <button
          onClick={markAttendance}
          disabled={loading}
          className="mt-8 w-full py-4 rounded-2xl text-white font-bold text-lg 
          bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 
          hover:scale-[1.02] transition-all duration-300 shadow-xl"
        >
          {loading ? "⏳ Processing..." : "📸 Capture & Mark Attendance"}
        </button>

        {/* Message */}
        {msg && (
          <p className="mt-6 text-center text-lg font-semibold text-white">
            {msg}
          </p>
        )}

        {/* Hidden canvas */}
        <canvas ref={canvasRef} className="hidden"></canvas>
      </div>
    </motion.div>
  );
}
