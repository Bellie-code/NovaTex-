import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

import { Toaster } from "react-hot-toast";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          borderRadius: "14px",
          background: "rgba(15, 23, 42, 0.95)",
          color: "white",
          border: "1px solid rgba(255,255,255,0.1)",
        },
      }}
    />
    <App />
  </React.StrictMode>
);
