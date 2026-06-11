export async function analyzeJob(targetRole, jobDescription) {
  const response = await fetch("/api/jobs/analyze", {
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
    throw new Error("The backend returned an invalid response.");
  }

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "Job analysis failed.";

    throw new Error(message);
  }

  return data;
}