export async function analyzeMatch(profile, job) {
  const response = await fetch("/api/matches/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      profile,
      job,
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The backend returned an invalid match response.");
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Job matching failed."
    );
  }

  return data;
}