console.log("🔥 ATTENDANCE PAGE UPDATED 🔥");

import React, { useEffect, useRef, useState } from "react";

const BACKEND_URL = "http://localhost:8000";

export default function Attendance({ token }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [employeeId, setEmployeeId] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const [challenge, setChallenge] = useState(null);
  const [challengePassed, setChallengePassed] = useState(false);

  const [isLive, setIsLive] = useState(false);
  const [spoofReason, setSpoofReason] = useState("");

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  // -----------------------------
  // Start Camera (Improved)
  // -----------------------------
  const startCamera = async () => {
    try {

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: "user"
        }
      });

      videoRef.current.srcObject = stream;

      setMsg("📷 Camera started. Fetching challenge...");
      fetchChallenge();

    } catch (err) {
      console.log(err);
      setMsg("❌ Camera permission denied!");
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
  };

  // -----------------------------
  // Capture Frame (Higher Quality)
  // -----------------------------
  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return null;
    if (video.videoWidth === 0 || video.videoHeight === 0) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg", 0.9);
  };

  // -----------------------------
  // Capture Multiple Frames
  // -----------------------------
  const captureFrames = async (count = 12, interval = 250) => {

    let frames = [];

    for (let i = 0; i < count; i++) {

      const frame = captureFrame();

      if (frame) frames.push(frame);

      await new Promise((resolve) => setTimeout(resolve, interval));

    }

    return frames;
  };

  // -----------------------------
  // Fetch Challenge
  // -----------------------------
  const fetchChallenge = async () => {

    try {

      const res = await fetch(`${BACKEND_URL}/api/spoof/challenge`);

      const data = await res.json();

      setChallenge(data);

      setMsg(`🧠 Challenge: ${data.challenge}`);

    } catch (err) {

      console.log(err);

      setMsg("❌ Failed to fetch challenge.");

    }

  };

  // -----------------------------
  // Spoof Check
  // -----------------------------
  const checkSpoof = async () => {

    try {

      const imageBase64 = captureFrame();

      if (!imageBase64) return;

      const res = await fetch(`${BACKEND_URL}/api/spoof/check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          image: imageBase64
        })
      });

      const data = await res.json();

      setIsLive(data.is_live);

      setSpoofReason(data.reason);

      return data.is_live;

    } catch (err) {

      console.log(err);

      setIsLive(false);

      setSpoofReason("Error calling spoof check");

      return false;

    }

  };

  // -----------------------------
  // Verify Challenge
  // -----------------------------
  const verifyChallenge = async () => {

    if (!challenge?.challenge_id) {
      setMsg("❌ Challenge not found. Refresh page.");
      return;
    }

    setLoading(true);

    setMsg("⏳ Preparing camera...");

    try {

      // Wait 1 second so face is stable
      await new Promise((r) => setTimeout(r, 1000));

      setMsg("⏳ Capturing frames...");

      const frames = await captureFrames(12, 250);

      if (frames.length < 5) {

        setMsg("❌ Not enough frames captured.");

        setLoading(false);

        return;

      }

      setMsg("⏳ Sending frames to backend...");

      const res = await fetch(`${BACKEND_URL}/api/spoof/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          challenge_id: challenge.challenge_id,
          frames: frames
        })
      });

      const data = await res.json();

      if (data.success === true) {

        setChallengePassed(true);

        setMsg("✅ Challenge Passed! You are LIVE.");

      } else {

        setChallengePassed(false);

        setMsg(`❌ Challenge Failed: ${data.reason || "Try again"}`);

      }

      setLoading(false);

    } catch (err) {

      console.log(err);

      setMsg("❌ Backend error verifying challenge.");

      setLoading(false);

    }

  };

  // -----------------------------
  // Mark Attendance
  // -----------------------------
  const markAttendance = async () => {

    if (!isLive) {

      alert("❌ Spoof detected. Attendance blocked.");

      return;

    }

    if (!challengePassed) {

      alert("❌ Challenge not passed. Attendance blocked.");

      return;

    }

    if (!employeeId) {

      alert("❌ Enter Employee ID first!");

      return;

    }

    try {

      setLoading(true);

      setMsg("⏳ Capturing frame for attendance...");

      const imageBase64 = captureFrame();

      if (!imageBase64) {

        setMsg("❌ Failed to capture frame.");

        setLoading(false);

        return;

      }

      setMsg("⏳ Sending attendance to backend...");

      const res = await fetch(`${BACKEND_URL}/api/attendance/mark`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          image_base64: imageBase64,
          device: "WEB_CAM"
        })
      });

      const data = await res.json();

      if (!res.ok) {

        setMsg(`❌ ${data.detail || "Attendance failed"}`);

        setLoading(false);

        return;

      }

      if (data.status === "SUCCESS") {

        setMsg(`✅ Attendance marked! Confidence: ${data.confidence.toFixed(2)}`);

      }
      else if (data.status === "ALREADY_MARKED") {

        setMsg("⚠ Attendance already marked today.");

      }
      else {

        setMsg(`❌ ${data.reason || "Face not recognized"}`);

      }

      setLoading(false);

    } catch (err) {

      console.log(err);

      setMsg("❌ Error connecting backend.");

      setLoading(false);

    }

  };

  // -----------------------------
  // Run spoof check every 2 sec
  // -----------------------------
  useEffect(() => {

    if (!challenge) return;

    const interval = setInterval(async () => {

      if (!challengePassed) {

        await checkSpoof();

      }

    }, 2000);

    return () => clearInterval(interval);

  }, [challenge, challengePassed]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0E14] via-[#1A1033] to-[#2D124F] p-10">

      <div className="w-full max-w-5xl bg-white/10 border border-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8">

        <h1 className="text-4xl font-bold text-white text-center mb-2">
          Mark Attendance
        </h1>

        <p className="text-gray-300 text-center mb-8">
          Complete liveness verification and mark attendance.
        </p>

        <div className="grid grid-cols-2 gap-6">

          <div className="rounded-3xl overflow-hidden border border-white/10 shadow-xl">

            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-[400px] object-cover"
            />

          </div>

          <div className="space-y-4">

            <input
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              placeholder="Employee ID (EMP301)"
              className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white outline-none border border-white/10 focus:border-purple-400"
            />

            {challenge && (
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10 text-white">

                <p className="text-lg font-semibold">
                  Challenge: <span className="text-pink-400">{challenge.challenge}</span>
                </p>

                <p className="text-sm text-gray-300">
                  Challenge ID: {challenge.challenge_id}
                </p>

                <p className="text-sm text-gray-300">
                  Expires in: {challenge.expires_in}s
                </p>

              </div>
            )}

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 text-white">

              <p className="text-lg font-semibold">
                Liveness: {isLive ? (
                  <span className="text-green-400">LIVE</span>
                ) : (
                  <span className="text-red-400">SPOOF</span>
                )}
              </p>

              {!isLive && spoofReason && (
                <p className="text-sm text-red-300 mt-1">
                  Reason: {spoofReason}
                </p>
              )}

              <p className="text-lg font-semibold mt-2">
                Challenge Passed: {challengePassed ? (
                  <span className="text-green-400">YES</span>
                ) : (
                  <span className="text-red-400">NO</span>
                )}
              </p>

            </div>

            <button
              onClick={verifyChallenge}
              disabled={loading || challengePassed}
              className="w-full py-4 rounded-2xl font-semibold text-white text-lg bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 hover:opacity-90 transition shadow-lg"
            >
              {loading ? "Verifying..." : "✅ Verify Challenge"}
            </button>

            <button
              onClick={markAttendance}
              disabled={!challengePassed || !isLive}
              className={`w-full py-4 rounded-2xl font-semibold text-white text-lg transition shadow-lg ${
                challengePassed && isLive
                  ? "bg-gradient-to-r from-green-500 to-emerald-600 hover:opacity-90"
                  : "bg-gray-600 cursor-not-allowed"
              }`}
            >
              📌 Mark Attendance
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