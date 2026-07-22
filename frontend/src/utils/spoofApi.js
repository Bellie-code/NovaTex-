const BACKEND_URL = "http://localhost:8000";

export async function getChallenge() {
  const res = await fetch(`${BACKEND_URL}/api/spoof/challenge`);
  if (!res.ok) throw new Error("Failed to get challenge");
  return res.json();
}

export async function verifyChallenge(challengeId, frames) {
  const res = await fetch(`${BACKEND_URL}/api/spoof/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      challenge_id: challengeId,
      frames: frames,
    }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Verify failed");
  return data;
}

export async function spoofCheck(singleFrame) {
  const res = await fetch(`${BACKEND_URL}/api/spoof/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: singleFrame }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Spoof check failed");
  return data;
}
