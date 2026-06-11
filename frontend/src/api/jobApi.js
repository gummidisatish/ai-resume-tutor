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

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Job analysis failed."
    );
  }

  return data;
}