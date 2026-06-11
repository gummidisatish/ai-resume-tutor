import { API_BASE_URL } from "./config.js";
export async function analyzeResume(file) {
  const formData = new FormData();
  formData.append("resume", file);

  const response = await fetch(`${API_BASE_URL}/api/tutor/course-plan`, {
    method: "POST",
    body: formData,
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The backend returned an invalid response.");
  }

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "Resume analysis failed.";

    throw new Error(message);
  }

  return data;
}