import { API_BASE_URL } from "./config.js";

export async function analyzeJob(targetRole, jobDescription) {
  const response = await fetch(`${API_BASE_URL}/api/jobs/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_role: targetRole,
      job_description: jobDescription,
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The backend returned an invalid job response.");
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Job analysis failed."
    );
  }

  return data;
}