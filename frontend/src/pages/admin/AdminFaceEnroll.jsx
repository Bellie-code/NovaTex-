import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { enrollFace } from "../../api/adminApi";

export default function AdminFaceEnroll() {

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const videoRef = useRef(null);

  const [employeeId, setEmployeeId] = useState(
    searchParams.get("employee") || ""
  );

  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // ==========================
  // START CAMERA
  // ==========================

  useEffect(() => {

    startCamera();

    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject
          .getTracks()
          .forEach(track => track.stop());
      }
    };

  }, []);

  const startCamera = async () => {

    try {

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

    } catch (err) {

      console.log(err);
      setMessage("Unable to access camera");

    }

  };

  // ==========================
  // CAPTURE IMAGE
  // ==========================

  const captureImage = () => {

    const canvas = document.createElement("canvas");

    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(videoRef.current, 0, 0);

    const base64 = canvas.toDataURL("image/jpeg");

    setImage(base64);

    setMessage("Face captured successfully");

  };

  // ==========================
  // ENROLL FACE
  // ==========================

  const submitFace = async () => {

    if (!image) {
      setMessage("Capture a face first.");
      return;
    }

    try {

      setLoading(true);

      await enrollFace(employeeId, image);

      setLoading(false);

      setMessage("Face enrolled successfully.");

      setTimeout(() => {

        navigate("/employees");

      }, 1200);

    } catch (err) {

      console.log(err);

      setLoading(false);

      setMessage(
        err?.response?.data?.detail || "Enrollment failed."
      );

    }

  };

  return (

    <div className="min-h-screen bg-gradient-to-br from-[#0B0E14] via-[#1A1033] to-[#2D124F] flex items-center justify-center p-8">

      <div className="w-full max-w-6xl bg-white/10 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl p-8">

        <h1 className="text-5xl font-bold text-white text-center">
          Face Enrollment
        </h1>

        <p className="text-center text-gray-300 mt-3 mb-8 text-xl">
          Capture a live face image and register employee details.
        </p>

        <div className="grid grid-cols-2 gap-8">

          {/* CAMERA */}

          <div>

            <video

              ref={videoRef}

              autoPlay

              playsInline

              className="w-full h-[450px] bg-black rounded-3xl object-cover"

            />

          </div>

          {/* RIGHT PANEL */}

          <div className="space-y-6">

            <input

              value={employeeId}

              onChange={(e)=>setEmployeeId(e.target.value)}

              placeholder="Employee ID"

              className="w-full rounded-2xl bg-white/10 border border-white/10 px-6 py-5 text-white outline-none placeholder-gray-400"

            />

            <button

              onClick={captureImage}

              className="w-full rounded-2xl py-5 bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 text-white font-bold text-xl"

            >
              📸 Capture Face
            </button>

            <button

              onClick={submitFace}

              disabled={loading}

              className="w-full rounded-2xl py-5 bg-green-600 hover:bg-green-700 text-white font-bold text-xl"

            >

              {loading ? "Enrolling..." : "Enroll Face"}

            </button>

            {message && (

              <div className="bg-white/10 rounded-2xl p-5 text-center text-white">

                {message}

              </div>

            )}

          </div>

        </div>

      </div>

    </div>

  );

}