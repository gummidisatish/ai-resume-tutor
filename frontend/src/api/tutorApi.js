import { API_BASE_URL } from "./config.js";
export async function generateCoursePlan(
  skill,
  targetRole,
  knowledgeLevel = "beginner"
) {
  const response = await fetch(`${API_BASE_URL}/api/tutor/course-plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      skill,
      target_role: targetRole,
      knowledge_level: knowledgeLevel,
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The backend returned an invalid tutor response."
    );
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "The AI tutor could not generate the course."
    );
  }

  return data;
}