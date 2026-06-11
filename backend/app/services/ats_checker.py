import re

from app.schemas.ats import ATSCheckItem, ATSCheckResult
from app.schemas.job import JobAnalysis
from app.schemas.resume import CandidateProfile
from app.services.job_matcher import (
    text_contains_skill,
    unique_skills,
)


ACTION_VERBS = {
    "achieved",
    "analysed",
    "analyzed",
    "automated",
    "built",
    "collaborated",
    "created",
    "deployed",
    "designed",
    "developed",
    "enhanced",
    "implemented",
    "improved",
    "integrated",
    "led",
    "managed",
    "optimized",
    "organised",
    "organized",
    "performed",
    "reduced",
    "resolved",
    "tested",
    "trained",
    "updated",
}


STANDARD_SECTIONS = {
    "education": [
        "education",
        "academic qualification",
        "academic qualifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
    ],
    "experience": [
        "experience",
        "work experience",
        "internship",
        "internships",
        "employment",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "courses",
        "training",
    ],
}


def create_check(
    name: str,
    score: int,
    maximum_score: int,
    message: str,
    suggestions: list[str] | None = None,
) -> ATSCheckItem:
    percentage = score / maximum_score if maximum_score else 0

    if percentage >= 0.75:
        status = "passed"
    elif percentage >= 0.4:
        status = "warning"
    else:
        status = "failed"

    return ATSCheckItem(
        name=name,
        status=status,
        score=score,
        maximum_score=maximum_score,
        message=message,
        suggestions=suggestions or [],
    )


def profile_to_text(profile: CandidateProfile) -> str:
    content = [
        profile.name,
        profile.location,
        profile.professional_summary,
        " ".join(profile.technical_skills),
        " ".join(profile.programming_languages),
        " ".join(profile.tools),
        " ".join(profile.soft_skills),
        " ".join(profile.achievements),
        " ".join(profile.courses),
        " ".join(profile.interests),
    ]

    for education in profile.education:
        content.extend(
            [
                education.degree,
                education.specialization,
                education.institution,
                education.location,
                education.score,
            ]
        )

    for project in profile.projects:
        content.extend(
            [
                project.name,
                project.description,
                " ".join(project.technologies),
                " ".join(project.features),
            ]
        )

    for experience in profile.experience:
        content.extend(
            [
                experience.role,
                experience.organization,
                experience.location,
                " ".join(experience.responsibilities),
                " ".join(experience.technologies),
            ]
        )

    for certification in profile.certifications:
        content.extend(
            [
                certification.name,
                certification.issuer,
            ]
        )

    return " ".join(
        item.strip()
        for item in content
        if item and item.strip()
    )


def check_contact_details(
    profile: CandidateProfile,
) -> ATSCheckItem:
    score = 0
    suggestions = []

    if profile.email.strip():
        score += 5
    else:
        suggestions.append(
            "Add a professional email address."
        )

    if profile.phone.strip():
        score += 5
    else:
        suggestions.append(
            "Add a valid phone number."
        )

    return create_check(
        name="Contact details",
        score=score,
        maximum_score=10,
        message=(
            "Email and phone number are available."
            if score == 10
            else "Some contact information is missing."
        ),
        suggestions=suggestions,
    )


def check_professional_links(
    profile: CandidateProfile,
) -> ATSCheckItem:
    links = [
        profile.linkedin,
        profile.github,
        profile.portfolio,
    ]

    available_links = sum(
        bool(link.strip())
        for link in links
    )

    score = min(available_links * 3, 6)

    suggestions = []

    if not profile.linkedin.strip():
        suggestions.append(
            "Add your LinkedIn profile."
        )

    if not profile.github.strip():
        suggestions.append(
            "Add GitHub if you have technical projects."
        )

    if not profile.portfolio.strip():
        suggestions.append(
            "Add a portfolio link if available."
        )

    return create_check(
        name="Professional links",
        score=score,
        maximum_score=6,
        message=f"{available_links} professional link(s) found.",
        suggestions=suggestions,
    )


def check_summary(
    profile: CandidateProfile,
) -> ATSCheckItem:
    summary = profile.professional_summary.strip()

    if len(summary) >= 80:
        score = 6
        message = "A detailed professional summary is present."
    elif len(summary) >= 30:
        score = 3
        message = "The professional summary is present but too short."
    else:
        score = 0
        message = "No useful professional summary was found."

    suggestions = []

    if score < 6:
        suggestions.append(
            "Add a 2–4 line role-focused professional summary."
        )

    return create_check(
        name="Professional summary",
        score=score,
        maximum_score=6,
        message=message,
        suggestions=suggestions,
    )


def check_standard_sections(
    resume_text: str,
) -> ATSCheckItem:
    normalized_text = resume_text.lower()

    found_sections = []

    for section, headings in STANDARD_SECTIONS.items():
        if any(
            heading in normalized_text
            for heading in headings
        ):
            found_sections.append(section)

    score = round(
        len(found_sections)
        / len(STANDARD_SECTIONS)
        * 8
    )

    missing_sections = [
        section.title()
        for section in STANDARD_SECTIONS
        if section not in found_sections
    ]

    return create_check(
        name="Standard résumé sections",
        score=score,
        maximum_score=8,
        message=(
            f"{len(found_sections)} of "
            f"{len(STANDARD_SECTIONS)} standard sections found."
        ),
        suggestions=[
            f"Add a clear {section} section."
            for section in missing_sections
        ],
    )


def check_skills(
    profile: CandidateProfile,
) -> ATSCheckItem:
    skills = unique_skills(
        [
            *profile.programming_languages,
            *profile.technical_skills,
            *profile.tools,
        ]
    )

    skill_count = len(skills)

    if skill_count >= 8:
        score = 12
    elif skill_count >= 4:
        score = 7
    elif skill_count >= 1:
        score = 3
    else:
        score = 0

    suggestions = []

    if score < 12:
        suggestions.extend(
            [
                "Add relevant technical skills using standard names.",
                "Prioritise skills required by the target job.",
            ]
        )

    return create_check(
        name="Technical skills",
        score=score,
        maximum_score=12,
        message=f"{skill_count} technical skill(s) identified.",
        suggestions=suggestions,
    )


def check_education(
    profile: CandidateProfile,
) -> ATSCheckItem:
    has_education = bool(profile.education)

    return create_check(
        name="Education",
        score=8 if has_education else 0,
        maximum_score=8,
        message=(
            "Education information is present."
            if has_education
            else "No education information was found."
        ),
        suggestions=(
            []
            if has_education
            else [
                "Add degree, institution, dates and score."
            ]
        ),
    )


def check_projects(
    profile: CandidateProfile,
) -> ATSCheckItem:
    project_count = len(profile.projects)

    detailed_projects = sum(
        bool(project.description.strip())
        and bool(project.technologies)
        for project in profile.projects
    )

    if project_count >= 2 and detailed_projects >= 2:
        score = 10
    elif project_count >= 1:
        score = 6
    else:
        score = 0

    suggestions = []

    if score < 10:
        suggestions.extend(
            [
                "Add at least two relevant projects.",
                "Explain the problem, implementation and result.",
                "Mention the technologies used.",
            ]
        )

    return create_check(
        name="Projects",
        score=score,
        maximum_score=10,
        message=(
            f"{project_count} project(s) found; "
            f"{detailed_projects} include descriptions and technologies."
        ),
        suggestions=suggestions,
    )


def check_experience(
    profile: CandidateProfile,
) -> ATSCheckItem:
    experience_count = len(profile.experience)
    project_count = len(profile.projects)

    if experience_count > 0:
        score = 10
        message = (
            f"{experience_count} experience record(s) found."
        )
        suggestions = []

    elif project_count >= 2:
        score = 7
        message = (
            "No work experience found, but projects provide "
            "useful evidence for a fresher."
        )
        suggestions = [
            "Add internships, freelance work or volunteering if available."
        ]

    else:
        score = 0
        message = (
            "No experience or strong project evidence was found."
        )
        suggestions = [
            "Add internships, projects, freelance work or volunteering."
        ]

    return create_check(
        name="Experience evidence",
        score=score,
        maximum_score=10,
        message=message,
        suggestions=suggestions,
    )


def check_action_verbs(
    profile: CandidateProfile,
) -> ATSCheckItem:
    content = profile_to_text(profile).lower()

    found_verbs = sorted(
        verb
        for verb in ACTION_VERBS
        if re.search(
            rf"\b{re.escape(verb)}\b",
            content,
        )
    )

    if len(found_verbs) >= 5:
        score = 8
    elif len(found_verbs) >= 2:
        score = 4
    else:
        score = 0

    suggestions = []

    if score < 8:
        suggestions.append(
            "Start résumé bullet points with verbs such as "
            "Developed, Built, Implemented, Improved or Automated."
        )

    return create_check(
        name="Action verbs",
        score=score,
        maximum_score=8,
        message=f"{len(found_verbs)} action verb(s) found.",
        suggestions=suggestions,
    )


def check_measurable_achievements(
    profile: CandidateProfile,
) -> ATSCheckItem:
    content = profile_to_text(profile)

    number_patterns = re.findall(
        r"(?<!\w)(?:\d+(?:\.\d+)?%?|\d+x)(?!\w)",
        content,
        flags=re.IGNORECASE,
    )

    measurable_count = len(number_patterns)

    if measurable_count >= 3:
        score = 8
    elif measurable_count >= 1:
        score = 4
    else:
        score = 0

    suggestions = []

    if score < 8:
        suggestions.extend(
            [
                "Add numbers, percentages, user counts or performance improvements.",
                "Do not invent metrics that cannot be verified.",
            ]
        )

    return create_check(
        name="Measurable achievements",
        score=score,
        maximum_score=8,
        message=f"{measurable_count} measurable value(s) found.",
        suggestions=suggestions,
    )


def build_job_keywords(
    job: JobAnalysis,
) -> list[str]:
    return unique_skills(
        [
            *job.required_skills,
            *job.preferred_skills,
            *job.programming_languages,
            *job.frameworks,
            *job.tools,
            *job.databases,
            *job.cloud_platforms,
            *job.knowledge_areas,
            *job.important_keywords,
        ]
    )


def check_job_keywords(
    profile: CandidateProfile,
    job: JobAnalysis,
    resume_text: str,
) -> tuple[ATSCheckItem, list[str], list[str]]:
    keywords = build_job_keywords(job)

    complete_text = (
        f"{profile_to_text(profile)} {resume_text}"
    )

    present_keywords = []
    missing_keywords = []

    for keyword in keywords:
        if text_contains_skill(keyword, complete_text):
            present_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if keywords:
        ratio = len(present_keywords) / len(keywords)
        score = round(ratio * 14)
    else:
        score = 0

    suggestions = [
        f"Add genuine résumé evidence for: {keyword}"
        for keyword in missing_keywords[:8]
    ]

    check = create_check(
        name="Target-job keywords",
        score=score,
        maximum_score=14,
        message=(
            f"{len(present_keywords)} of "
            f"{len(keywords)} important keyword(s) found."
        ),
        suggestions=suggestions,
    )

    return check, present_keywords, missing_keywords


def run_ats_check(
    profile: CandidateProfile,
    job: JobAnalysis,
    resume_text: str,
) -> ATSCheckResult:
    checks = [
        check_contact_details(profile),
        check_professional_links(profile),
        check_summary(profile),
        check_standard_sections(resume_text),
        check_skills(profile),
        check_education(profile),
        check_projects(profile),
        check_experience(profile),
        check_action_verbs(profile),
        check_measurable_achievements(profile),
    ]

    (
        keyword_check,
        present_keywords,
        missing_keywords,
    ) = check_job_keywords(
        profile=profile,
        job=job,
        resume_text=resume_text,
    )

    checks.append(keyword_check)

    ats_score = sum(
        check.score
        for check in checks
    )

    ats_score = max(
        0,
        min(ats_score, 100),
    )

    if ats_score >= 85:
        rating = "Excellent"
    elif ats_score >= 70:
        rating = "Good"
    elif ats_score >= 55:
        rating = "Needs improvement"
    else:
        rating = "Weak"

    passed_count = sum(
        check.status == "passed"
        for check in checks
    )

    warning_count = sum(
        check.status == "warning"
        for check in checks
    )

    failed_count = sum(
        check.status == "failed"
        for check in checks
    )

    strengths = [
        check.message
        for check in checks
        if check.status == "passed"
    ]

    priority_improvements = []

    for check in checks:
        if check.status == "failed":
            priority_improvements.extend(
                check.suggestions
            )

    for check in checks:
        if check.status == "warning":
            priority_improvements.extend(
                check.suggestions
            )

    priority_improvements = list(
        dict.fromkeys(priority_improvements)
    )[:10]

    return ATSCheckResult(
        ats_score=ats_score,
        rating=rating,
        passed_count=passed_count,
        warning_count=warning_count,
        failed_count=failed_count,
        checks=checks,
        present_keywords=present_keywords,
        missing_keywords=missing_keywords,
        strengths=strengths,
        priority_improvements=priority_improvements,
    )