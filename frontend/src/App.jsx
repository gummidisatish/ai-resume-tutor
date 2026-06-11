import { useState } from "react";

import { checkATS } from "./api/atsApi.js";
import { analyzeJob } from "./api/jobApi.js";
import { analyzeMatch } from "./api/matchApi.js";
import { analyzeResume } from "./api/resumeApi.js";
import { generateCoursePlan } from "./api/tutorApi.js";

function uniqueItems(items = []) {
  return [...new Set(items.filter(Boolean))];
}

function SkillChips({ items }) {
  const cleanedItems = uniqueItems(items);

  if (!cleanedItems.length) {
    return <p>No information found.</p>;
  }

  return (
    <div className="skills">
      {cleanedItems.map((item, index) => (
        <span key={`${item}-${index}`}>{item}</span>
      ))}
    </div>
  );
}

function ResultList({
  items,
  emptyMessage = "No information found.",
}) {
  if (!items?.length) {
    return emptyMessage ? <p>{emptyMessage}</p> : null;
  }

  return (
    <ul className="result-list">
      {items.map((item, index) => (
        <li key={`${String(item)}-${index}`}>{item}</li>
      ))}
    </ul>
  );
}

function App() {
  const [file, setFile] = useState(null);

  const [resumeResult, setResumeResult] = useState(null);
  const [resumeError, setResumeError] = useState("");
  const [resumeLoading, setResumeLoading] = useState(false);

  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [jobResult, setJobResult] = useState(null);
  const [jobError, setJobError] = useState("");
  const [jobLoading, setJobLoading] = useState(false);

  const [matchResult, setMatchResult] = useState(null);
  const [matchError, setMatchError] = useState("");
  const [matchLoading, setMatchLoading] = useState(false);

  const [atsResult, setAtsResult] = useState(null);
  const [atsError, setAtsError] = useState("");
  const [atsLoading, setAtsLoading] = useState(false);

  const [selectedSkill, setSelectedSkill] = useState("");
  const [knowledgeLevel, setKnowledgeLevel] =
    useState("beginner");

  const [tutorResult, setTutorResult] = useState(null);
  const [tutorError, setTutorError] = useState("");
  const [tutorLoading, setTutorLoading] = useState(false);
  const [openModuleNumber, setOpenModuleNumber] = useState(null);

  const profile = resumeResult?.profile;

  const combinedSkills = profile
    ? uniqueItems([
        ...(profile.programming_languages || []),
        ...(profile.technical_skills || []),
        ...(profile.tools || []),
      ])
    : [];

  function resetTutor() {
  setSelectedSkill("");
  setKnowledgeLevel("beginner");
  setTutorResult(null);
  setTutorError("");
  setTutorLoading(false);
  setOpenModuleNumber(null);
}

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0] || null;

    setFile(selectedFile);

    setResumeResult(null);
    setResumeError("");

    setTargetRole("");
    setJobDescription("");

    setJobResult(null);
    setJobError("");

    setMatchResult(null);
    setMatchError("");

    setAtsResult(null);
    setAtsError("");

    resetTutor();
  }

  async function handleAnalyzeResume() {
    if (!file) {
      setResumeError("Please select a PDF or DOCX résumé.");
      return;
    }

    const filename = file.name.toLowerCase();

    const validFile =
      filename.endsWith(".pdf") ||
      filename.endsWith(".docx");

    if (!validFile) {
      setResumeError(
        "Only PDF and DOCX files are supported."
      );
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setResumeError(
        "The résumé must be smaller than 5 MB."
      );
      return;
    }

    setResumeLoading(true);
    setResumeError("");
    setResumeResult(null);

    try {
      const data = await analyzeResume(file);
      setResumeResult(data);
    } catch (error) {
      setResumeError(
        error.message || "Résumé analysis failed."
      );
    } finally {
      setResumeLoading(false);
    }
  }

  async function handleAnalyzeJob(event) {
    event.preventDefault();

    if (!profile) {
      setJobError("Please analyse a résumé first.");
      return;
    }

    const cleanedDescription = jobDescription.trim();
    const cleanedRole = targetRole.trim();

    if (cleanedDescription.length < 50) {
      setJobError(
        "Please enter a complete job description with at least 50 characters."
      );
      return;
    }

    setJobLoading(true);
    setJobError("");

    setJobResult(null);

    setMatchResult(null);
    setMatchError("");

    setAtsResult(null);
    setAtsError("");

    resetTutor();

    try {
      const analyzedJob = await analyzeJob(
        cleanedRole,
        cleanedDescription
      );

      setJobResult(analyzedJob);
      setJobLoading(false);

      setMatchLoading(true);
      setAtsLoading(true);

      const [matchResponse, atsResponse] =
        await Promise.allSettled([
          analyzeMatch(profile, analyzedJob),

          checkATS(
            profile,
            analyzedJob,
            resumeResult?.resume_text || ""
          ),
        ]);

      if (matchResponse.status === "fulfilled") {
        setMatchResult(matchResponse.value);
      } else {
        setMatchError(
          matchResponse.reason?.message ||
            "Job matching failed."
        );
      }

      if (atsResponse.status === "fulfilled") {
        setAtsResult(atsResponse.value);
      } else {
        setAtsError(
          atsResponse.reason?.message ||
            "ATS analysis failed."
        );
      }
    } catch (error) {
      setJobError(
        error.message || "Target-job analysis failed."
      );
    } finally {
      setJobLoading(false);
      setMatchLoading(false);
      setAtsLoading(false);
    }
  }

  async function handleGenerateCourse(skill) {
    if (!skill) {
      setTutorError("Please select a missing skill.");
      return;
    }

    const role =
      matchResult?.target_role ||
      jobResult?.target_role ||
      targetRole ||
      "Target Job";

    setSelectedSkill(skill);
    setTutorLoading(true);
    setTutorError("");
    setTutorResult(null);

    try {
      const course = await generateCoursePlan(
        skill,
        role,
        knowledgeLevel
      );

      setTutorResult(course);
      setOpenModuleNumber(course.modules?.[0]?.module_number || 1);

      window.setTimeout(() => {
        document
          .getElementById("ai-tutor")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);
    } catch (error) {
      setTutorError(
        error.message ||
          "The AI tutor could not create the course."
      );
    } finally {
      setTutorLoading(false);
    }
  }

  function resetApplication() {
    setFile(null);

    setResumeResult(null);
    setResumeError("");
    setResumeLoading(false);

    setTargetRole("");
    setJobDescription("");

    setJobResult(null);
    setJobError("");
    setJobLoading(false);

    setMatchResult(null);
    setMatchError("");
    setMatchLoading(false);

    setAtsResult(null);
    setAtsError("");
    setAtsLoading(false);

    resetTutor();
  }

  return (
    <main className="page">
      <section className="container">
        <header className="header">
          <span className="badge">AI Resume Tutor</span>

          <h1>AI Resume Parser</h1>

          <p>
            Analyse your résumé, compare it with a target
            job, check ATS compatibility and learn missing
            career skills.
          </p>
        </header>

        {!profile && (
          <section className="upload-card">
            <label className="file-box">
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
              />

              <strong>
                {file
                  ? file.name
                  : "Choose your résumé"}
              </strong>

              <span>
                PDF or DOCX, maximum size 5 MB
              </span>
            </label>

            <button
              type="button"
              onClick={handleAnalyzeResume}
              disabled={resumeLoading}
            >
              {resumeLoading
                ? "Analysing résumé..."
                : "Analyse Resume"}
            </button>

            {resumeLoading && (
              <div className="loading-message">
                <div className="spinner" />

                <div>
                  <strong>
                    Creating your candidate profile
                  </strong>

                  <p>
                    Extracting and analysing résumé
                    information.
                  </p>
                </div>
              </div>
            )}

            {resumeError && (
              <p className="error">{resumeError}</p>
            )}
          </section>
        )}

        {profile && (
          <>
            <section className="profile">
              <div className="profile-heading">
                <div>
                  <span className="success">
                    Résumé analysed successfully
                  </span>

                  <h2>
                    {profile.name ||
                      "Candidate Profile"}
                  </h2>

                  <p>
                    {profile.location ||
                      "Location not provided"}
                  </p>
                </div>

                <button
                  type="button"
                  className="secondary"
                  onClick={resetApplication}
                >
                  Upload another résumé
                </button>
              </div>

              <div className="grid">
                <article className="card">
                  <h3>Contact details</h3>

                  <p>
                    <strong>Email:</strong>{" "}
                    {profile.email || "Not provided"}
                  </p>

                  <p>
                    <strong>Phone:</strong>{" "}
                    {profile.phone || "Not provided"}
                  </p>

                  <p>
                    <strong>LinkedIn:</strong>{" "}
                    {profile.linkedin || "Not provided"}
                  </p>

                  <p>
                    <strong>GitHub:</strong>{" "}
                    {profile.github || "Not provided"}
                  </p>

                  <p>
                    <strong>Portfolio:</strong>{" "}
                    {profile.portfolio ||
                      "Not provided"}
                  </p>
                </article>

                <article className="card">
                  <h3>Professional summary</h3>

                  <p>
                    {profile.professional_summary ||
                      "No professional summary was found."}
                  </p>
                </article>

                <article className="card full-width">
                  <h3>Skills</h3>

                  <SkillChips
                    items={combinedSkills}
                  />
                </article>

                <article className="card full-width">
                  <h3>Education</h3>

                  {profile.education?.length ? (
                    profile.education.map(
                      (education, index) => (
                        <div
                          className="item"
                          key={index}
                        >
                          <strong>
                            {education.degree ||
                              "Degree"}

                            {education.specialization
                              ? ` — ${education.specialization}`
                              : ""}
                          </strong>

                          <p>
                            {education.institution ||
                              "Institution not provided"}
                          </p>

                          <small>
                            {[
                              education.start_year,
                              education.end_year,
                            ]
                              .filter(Boolean)
                              .join(" - ")}

                            {education.score
                              ? ` · ${education.score}`
                              : ""}
                          </small>
                        </div>
                      )
                    )
                  ) : (
                    <p>
                      No education information was
                      found.
                    </p>
                  )}
                </article>

                <article className="card full-width">
                  <h3>Projects</h3>

                  {profile.projects?.length ? (
                    profile.projects.map(
                      (project, index) => (
                        <div
                          className="item"
                          key={index}
                        >
                          <strong>
                            {project.name ||
                              "Unnamed project"}
                          </strong>

                          <p>
                            {project.description ||
                              "No project description provided."}
                          </p>

                          <SkillChips
                            items={
                              project.technologies || []
                            }
                          />
                        </div>
                      )
                    )
                  ) : (
                    <p>No projects were found.</p>
                  )}
                </article>

                <article className="card full-width">
                  <h3>Experience</h3>

                  {profile.experience?.length ? (
                    profile.experience.map(
                      (experience, index) => (
                        <div
                          className="item"
                          key={index}
                        >
                          <strong>
                            {experience.role ||
                              "Role not provided"}
                          </strong>

                          <p>
                            {experience.organization ||
                              "Organisation not provided"}
                          </p>

                          <small>
                            {[
                              experience.start_date,
                              experience.end_date,
                            ]
                              .filter(Boolean)
                              .join(" - ")}
                          </small>

                          <ResultList
                            items={
                              experience.responsibilities
                            }
                            emptyMessage=""
                          />
                        </div>
                      )
                    )
                  ) : (
                    <p>
                      No work experience was found.
                    </p>
                  )}
                </article>

                <article className="card">
                  <h3>Certifications</h3>

                  {profile.certifications?.length ? (
                    profile.certifications.map(
                      (certification, index) => (
                        <div
                          className="item"
                          key={index}
                        >
                          <strong>
                            {certification.name ||
                              "Unnamed certification"}
                          </strong>

                          <p>
                            {certification.issuer ||
                              "Issuer not provided"}
                          </p>
                        </div>
                      )
                    )
                  ) : (
                    <p>
                      No certifications were found.
                    </p>
                  )}
                </article>

                <article className="card">
                  <h3>Achievements</h3>

                  <ResultList
                    items={profile.achievements}
                    emptyMessage="No achievements were found."
                  />
                </article>
              </div>
            </section>

            <section className="target-job-section">
              <div className="section-title">
                <span className="badge">
                  Next Step
                </span>

                <h2>Analyse your target job</h2>

                <p>
                  Paste the complete job description to
                  identify the skills and qualifications
                  required by the employer.
                </p>
              </div>

              <form
                className="job-form-card"
                onSubmit={handleAnalyzeJob}
              >
                <div className="form-group">
                  <label htmlFor="targetRole">
                    Target role
                  </label>

                  <input
                    id="targetRole"
                    type="text"
                    value={targetRole}
                    onChange={(event) =>
                      setTargetRole(
                        event.target.value
                      )
                    }
                    placeholder="Example: Python Backend Developer"
                    maxLength={150}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="jobDescription">
                    Job description
                  </label>

                  <textarea
                    id="jobDescription"
                    value={jobDescription}
                    onChange={(event) =>
                      setJobDescription(
                        event.target.value
                      )
                    }
                    placeholder="Paste the complete job description here..."
                    rows={12}
                    maxLength={30000}
                  />
                </div>

                <div className="character-count">
                  {jobDescription.length} / 30000
                  characters
                </div>

                <button
                  type="submit"
                  disabled={
                    jobLoading ||
                    matchLoading ||
                    atsLoading
                  }
                >
                  {jobLoading
                    ? "Analysing target job..."
                    : matchLoading || atsLoading
                      ? "Preparing results..."
                      : "Analyse Target Job"}
                </button>

                {jobLoading && (
                  <div className="loading-message">
                    <div className="spinner" />

                    <div>
                      <strong>
                        Reading job requirements
                      </strong>

                      <p>
                        Identifying skills, tools and
                        qualifications.
                      </p>
                    </div>
                  </div>
                )}

                {jobError && (
                  <p className="error">
                    {jobError}
                  </p>
                )}
              </form>
            </section>

            {jobResult && (
              <section className="job-result-section">
                <div className="job-result-heading">
                  <span className="success">
                    Job analysed successfully
                  </span>

                  <h2>
                    {jobResult.target_role ||
                      targetRole ||
                      "Target Job"}
                  </h2>

                  <p>
                    {jobResult.company_name ||
                      "Company not specified"}
                  </p>
                </div>

                <div className="job-meta-grid">
                  <article className="card">
                    <h3>Experience level</h3>

                    <p>
                      {jobResult.experience_level ||
                        "Not specified"}
                    </p>
                  </article>

                  <article className="card">
                    <h3>Employment type</h3>

                    <p>
                      {jobResult.employment_type ||
                        "Not specified"}
                    </p>
                  </article>

                  <article className="card">
                    <h3>Job location</h3>

                    <p>
                      {jobResult.location ||
                        "Not specified"}
                    </p>
                  </article>
                </div>

                <div className="grid">
                  <article className="card full-width">
                    <h3>Job summary</h3>

                    <p>
                      {jobResult.job_summary ||
                        "No job summary was generated."}
                    </p>
                  </article>

                  <article className="card">
                    <h3>Required skills</h3>

                    <SkillChips
                      items={
                        jobResult.required_skills
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Preferred skills</h3>

                    <SkillChips
                      items={
                        jobResult.preferred_skills
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Programming languages</h3>

                    <SkillChips
                      items={
                        jobResult.programming_languages
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Frameworks</h3>

                    <SkillChips
                      items={jobResult.frameworks}
                    />
                  </article>

                  <article className="card">
                    <h3>Tools</h3>

                    <SkillChips
                      items={jobResult.tools}
                    />
                  </article>

                  <article className="card">
                    <h3>Databases</h3>

                    <SkillChips
                      items={jobResult.databases}
                    />
                  </article>

                  <article className="card">
                    <h3>Cloud platforms</h3>

                    <SkillChips
                      items={
                        jobResult.cloud_platforms
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Knowledge areas</h3>

                    <SkillChips
                      items={
                        jobResult.knowledge_areas
                      }
                    />
                  </article>

                  <article className="card full-width">
                    <h3>Responsibilities</h3>

                    <ResultList
                      items={
                        jobResult.responsibilities
                      }
                      emptyMessage="No responsibilities were identified."
                    />
                  </article>

                  <article className="card">
                    <h3>
                      Education requirements
                    </h3>

                    <ResultList
                      items={
                        jobResult.education_requirements
                      }
                      emptyMessage="No education requirements were found."
                    />
                  </article>

                  <article className="card">
                    <h3>
                      Experience requirements
                    </h3>

                    <ResultList
                      items={
                        jobResult.experience_requirements
                      }
                      emptyMessage="No experience requirements were found."
                    />
                  </article>

                  <article className="card full-width">
                    <h3>Important ATS keywords</h3>

                    <SkillChips
                      items={
                        jobResult.important_keywords
                      }
                    />
                  </article>
                </div>
              </section>
            )}

            {matchLoading && (
              <div className="loading-message section-loading">
                <div className="spinner" />

                <div>
                  <strong>
                    Comparing résumé with the job
                  </strong>

                  <p>
                    Checking matching, partial and
                    missing skills.
                  </p>
                </div>
              </div>
            )}

            {matchError && (
              <p className="error">
                {matchError}
              </p>
            )}

            {matchResult && (
              <section className="match-result-section">
                <div className="section-title">
                  <span className="badge">
                    Job Match
                  </span>

                  <h2>
                    Résumé compatibility analysis
                  </h2>

                  <p>
                    This result compares the skills
                    evidenced in your résumé with the
                    requirements of the target job.
                  </p>
                </div>

                <div className="match-overview">
                  <article className="score-card">
                    <div
                      className="score-circle"
                      style={{
                        "--score": `${
                          matchResult.match_percentage *
                          3.6
                        }deg`,
                      }}
                    >
                      <div className="score-circle-inner">
                        <strong>
                          {
                            matchResult.match_percentage
                          }
                          %
                        </strong>

                        <span>Job match</span>
                      </div>
                    </div>

                    <div className="score-description">
                      <h3>
                        {matchResult.target_role ||
                          targetRole ||
                          "Target Job"}
                      </h3>

                      <p>
                        Based on required skills,
                        preferred skills and résumé
                        evidence.
                      </p>
                    </div>
                  </article>

                  <div className="match-statistics">
                    <article>
                      <span>Required skills</span>

                      <strong>
                        {
                          matchResult.required_skill_count
                        }
                      </strong>
                    </article>

                    <article className="matched-stat">
                      <span>Matching skills</span>

                      <strong>
                        {matchResult.matched_count}
                      </strong>
                    </article>

                    <article className="partial-stat">
                      <span>Partial evidence</span>

                      <strong>
                        {matchResult.partial_count}
                      </strong>
                    </article>

                    <article className="missing-stat">
                      <span>Missing skills</span>

                      <strong>
                        {matchResult.missing_count}
                      </strong>
                    </article>
                  </div>
                </div>

                <div className="grid match-grid">
                  <article className="card skill-status-card matched-card">
                    <div className="status-heading">
                      <div>
                        <span className="status-icon">
                          ✓
                        </span>

                        <h3>Matching skills</h3>
                      </div>

                      <span className="count-badge">
                        {matchResult.matching_skills
                          ?.length || 0}
                      </span>
                    </div>

                    {matchResult.matching_skills
                      ?.length ? (
                      <div className="evidence-list">
                        {matchResult.matching_skills.map(
                          (item, index) => (
                            <div
                              className="evidence-item"
                              key={index}
                            >
                              <strong>
                                {item.skill}
                              </strong>

                              <ResultList
                                items={item.evidence}
                                emptyMessage=""
                              />
                            </div>
                          )
                        )}
                      </div>
                    ) : (
                      <p>
                        No directly matching skills were
                        found.
                      </p>
                    )}
                  </article>

                  <article className="card skill-status-card partial-card">
                    <div className="status-heading">
                      <div>
                        <span className="status-icon">
                          !
                        </span>

                        <h3>
                          Partially evidenced
                        </h3>
                      </div>

                      <span className="count-badge">
                        {matchResult
                          .partially_evidenced_skills
                          ?.length || 0}
                      </span>
                    </div>

                    {matchResult
                      .partially_evidenced_skills
                      ?.length ? (
                      <div className="evidence-list">
                        {matchResult.partially_evidenced_skills.map(
                          (item, index) => (
                            <div
                              className="evidence-item"
                              key={index}
                            >
                              <strong>
                                {item.skill}
                              </strong>

                              <ResultList
                                items={item.evidence}
                                emptyMessage=""
                              />
                            </div>
                          )
                        )}
                      </div>
                    ) : (
                      <p>
                        No partially evidenced skills
                        were found.
                      </p>
                    )}
                  </article>

                  <article className="card skill-status-card missing-card">
                    <div className="status-heading">
                      <div>
                        <span className="status-icon">
                          ×
                        </span>

                        <h3>Missing skills</h3>
                      </div>

                      <span className="count-badge">
                        {matchResult.missing_skills
                          ?.length || 0}
                      </span>
                    </div>

                    {matchResult.missing_skills
                      ?.length ? (
                      <div className="missing-skill-list">
                        {matchResult.missing_skills.map(
                          (skill, index) => (
                            <div
                              className="missing-skill-item"
                              key={index}
                            >
                              <div>
                                <strong>
                                  {skill}
                                </strong>

                                <span>
                                  Not evidenced in your
                                  résumé
                                </span>
                              </div>

                              <button
                                type="button"
                                className="learn-button"
                                onClick={() =>
                                  handleGenerateCourse(
                                    skill
                                  )
                                }
                                disabled={
                                  tutorLoading
                                }
                              >
                                {tutorLoading &&
                                selectedSkill ===
                                  skill
                                  ? "Creating..."
                                  : "Learn now"}
                              </button>
                            </div>
                          )
                        )}
                      </div>
                    ) : (
                      <p>
                        No required skills are missing.
                      </p>
                    )}
                  </article>

                  <article className="card skill-status-card preferred-card">
                    <div className="status-heading">
                      <div>
                        <span className="status-icon">
                          +
                        </span>

                        <h3>
                          Missing preferred skills
                        </h3>
                      </div>

                      <span className="count-badge">
                        {matchResult
                          .missing_preferred_skills
                          ?.length || 0}
                      </span>
                    </div>

                    <SkillChips
                      items={
                        matchResult.missing_preferred_skills
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Candidate strengths</h3>

                    <ResultList
                      items={matchResult.strengths}
                      emptyMessage="No major strengths were identified."
                    />
                  </article>

                  <article className="card">
                    <h3>
                      Recommended next steps
                    </h3>

                    <ResultList
                      items={matchResult.next_steps}
                      emptyMessage="No additional steps are required."
                    />
                  </article>
                </div>
              </section>
            )}

            {atsLoading && (
              <div className="loading-message section-loading">
                <div className="spinner" />

                <div>
                  <strong>
                    Checking ATS compatibility
                  </strong>

                  <p>
                    Reviewing sections, keywords,
                    projects and achievements.
                  </p>
                </div>
              </div>
            )}

            {atsError && (
              <p className="error">{atsError}</p>
            )}

            {atsResult && (
              <section className="ats-result-section">
                <div className="section-title">
                  <span className="badge">
                    ATS Checker
                  </span>

                  <h2>ATS résumé analysis</h2>

                  <p>
                    This score checks résumé structure
                    and keyword alignment for the
                    selected job.
                  </p>
                </div>

                <div className="ats-overview">
                  <article className="ats-score-card">
                    <strong>
                      {atsResult.ats_score}%
                    </strong>

                    <span>ATS Score</span>

                    <p>{atsResult.rating}</p>
                  </article>

                  <div className="ats-statistics">
                    <article className="ats-passed">
                      <span>Passed</span>

                      <strong>
                        {atsResult.passed_count}
                      </strong>
                    </article>

                    <article className="ats-warning">
                      <span>Warnings</span>

                      <strong>
                        {atsResult.warning_count}
                      </strong>
                    </article>

                    <article className="ats-failed">
                      <span>Failed</span>

                      <strong>
                        {atsResult.failed_count}
                      </strong>
                    </article>
                  </div>
                </div>

                <div className="ats-check-list">
                  {atsResult.checks?.map(
                    (check, index) => (
                      <article
                        className={`ats-check ats-${check.status}`}
                        key={index}
                      >
                        <div className="ats-check-heading">
                          <div>
                            <h3>{check.name}</h3>

                            <p>{check.message}</p>
                          </div>

                          <strong>
                            {check.score}/
                            {check.maximum_score}
                          </strong>
                        </div>

                        <ResultList
                          items={check.suggestions}
                          emptyMessage=""
                        />
                      </article>
                    )
                  )}
                </div>

                <div className="grid">
                  <article className="card">
                    <h3>
                      Present job keywords
                    </h3>

                    <SkillChips
                      items={
                        atsResult.present_keywords
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>
                      Missing job keywords
                    </h3>

                    <SkillChips
                      items={
                        atsResult.missing_keywords
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Résumé strengths</h3>

                    <ResultList
                      items={atsResult.strengths}
                      emptyMessage="No major ATS strengths were identified."
                    />
                  </article>

                  <article className="card">
                    <h3>
                      Priority improvements
                    </h3>

                    <ResultList
                      items={
                        atsResult.priority_improvements
                      }
                      emptyMessage="No major improvements are currently required."
                    />
                  </article>
                </div>
              </section>
            )}

            {tutorLoading && (
              <div className="loading-message section-loading">
                <div className="spinner" />

                <div>
                  <strong>
                    Creating your {selectedSkill} course
                  </strong>

                  <p>
                    Building modules, practice tasks and
                    interview questions.
                  </p>
                </div>
              </div>
            )}

            {tutorError && (
              <p className="error">
                {tutorError}
              </p>
            )}

            {tutorResult && (
              <section
                className="tutor-result-section"
                id="ai-tutor"
              >
                <div className="tutor-heading">
                  <div>
                    <span className="badge">
                      AI Course Tutor
                    </span>

                    <h2>
                      {tutorResult.course_title}
                    </h2>

                    <p>
                      {
                        tutorResult.course_description
                      }
                    </p>
                  </div>

                  <button
                    type="button"
                    className="secondary"
                    onClick={resetTutor}
                  >
                    Close course
                  </button>
                </div>

                <div className="tutor-controls">
                  <div className="form-group">
                    <label htmlFor="knowledgeLevel">
                      Knowledge level
                    </label>

                    <select
                      id="knowledgeLevel"
                      value={knowledgeLevel}
                      onChange={(event) =>
                        setKnowledgeLevel(
                          event.target.value
                        )
                      }
                    >
                      <option value="beginner">
                        Beginner
                      </option>

                      <option value="basic">
                        Basic knowledge
                      </option>

                      <option value="diagnostic">
                        Assess and teach
                      </option>
                    </select>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleGenerateCourse(
                        selectedSkill
                      )
                    }
                    disabled={tutorLoading}
                  >
                    Regenerate course
                  </button>
                </div>

                <div className="tutor-summary-grid">
                  <article className="card">
                    <h3>Skill</h3>

                    <p>{tutorResult.skill}</p>
                  </article>

                  <article className="card">
                    <h3>Target role</h3>

                    <p>
                      {tutorResult.target_role ||
                        targetRole ||
                        "Not specified"}
                    </p>
                  </article>

                  <article className="card">
                    <h3>Current level</h3>

                    <p>
                      {
                        tutorResult.knowledge_level
                      }
                    </p>
                  </article>
                </div>

                <div className="grid">
                  <article className="card">
                    <h3>Prerequisites</h3>

                    <SkillChips
                      items={
                        tutorResult.prerequisites
                      }
                    />
                  </article>

                  <article className="card">
                    <h3>Learning outcomes</h3>

                    <ResultList
                      items={
                        tutorResult.learning_outcomes
                      }
                      emptyMessage="No learning outcomes were provided."
                    />
                  </article>
                </div>

                <div className="course-modules">
                <h2>Course modules</h2>

    {tutorResult.modules?.length ? (
    tutorResult.modules.map((module, index) => {
      const moduleNumber = module.module_number || index + 1;
      const isOpen = openModuleNumber === moduleNumber;

      return (
        <article
          className={`course-module ${isOpen ? "module-open" : ""}`}
          key={`${moduleNumber}-${index}`}
        >
          <button
            type="button"
            className="module-toggle"
            onClick={() =>
              setOpenModuleNumber(isOpen ? null : moduleNumber)
            }
          >
            <div className="module-number">{moduleNumber}</div>

            <div className="module-title-area">
              <h3>{module.title}</h3>
              <p>{module.objective}</p>
            </div>

            <span className="module-arrow">
              {isOpen ? "−" : "+"}
            </span>
          </button>

          {isOpen && (
            <div className="module-content">
              <div className="module-time">
                {module.estimated_minutes} minutes
              </div>

              <h4>Topics</h4>

              <SkillChips items={module.topics} />

              <div className="practice-task">
                <strong>Practice task</strong>

                <p>{module.practice_task}</p>
              </div>
            </div>
          )}
        </article>
      );
    })
  ) : (
    <p>No course modules were generated.</p>
  )}
</div>

                <div className="grid">
                  <article className="card full-width final-project-card">
                    <h3>Final project</h3>

                    <p>
                      {tutorResult.final_project ||
                        "No final project was generated."}
                    </p>
                  </article>

                  <article className="card full-width">
                    <h3>Interview questions</h3>

                    <ResultList
                      items={
                        tutorResult.interview_questions
                      }
                      emptyMessage="No interview questions were generated."
                    />
                  </article>
                </div>
              </section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default App;