import { API_BASE_URL } from "./config.js";

export async function analyzeResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/resumes/analyze`, {
    method: "POST",
    body: formData,
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned invalid response. Status: ${response.status}`
    );
  }

  if (!response.ok) {
    console.log("Resume API error:", data);

    if (typeof data.detail === "string") {
      throw new Error(data.detail);
    }

    throw new Error(
      `Resume analysis failed. Status: ${response.status}. Details: ${JSON.stringify(
        data.detail || data
      )}`
    );
  }

  return data;
}