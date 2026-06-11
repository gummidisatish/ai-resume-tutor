import { API_BASE_URL } from "./config.js";

export async function checkATS(profile, job, resumeText) {
  const response = await fetch(`${API_BASE_URL}/api/ats/check`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      profile,
      job,
      resume_text: resumeText,
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The backend returned an invalid ATS response.");
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "ATS analysis failed."
    );
  }

  return data;
}