import re
from collections import defaultdict

from app.schemas.job import JobAnalysis
from app.schemas.match import JobMatchResult, SkillMatchItem
from app.schemas.resume import CandidateProfile


SKILL_ALIASES = {
    "react js": "react",
    "react.js": "react",
    "reactjs": "react",

    "node js": "node.js",
    "nodejs": "node.js",

    "postgre sql": "postgresql",
    "postgres": "postgresql",

    "rest api": "rest apis",
    "restful api": "rest apis",
    "restful apis": "rest apis",

    "fast api": "fastapi",

    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",

    "machine learning": "machine learning",
    "ml": "machine learning",

    "artificial intelligence": "ai",

    "amazon web services": "aws",
    "google cloud platform": "gcp",

    "structured query language": "sql",

    "html5": "html",
    "css3": "css",

    "javascript es6": "javascript",
    "js": "javascript",

    "git hub": "github",
}


def basic_normalize(value: str) -> str:
    """Convert text into a standard lowercase comparison format."""

    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9+#.\-]+",
        " ",
        value,
    )

    return " ".join(value.split())


def normalize_skill(value: str) -> str:
    """Normalize a skill and apply known aliases."""

    normalized = basic_normalize(value)

    return SKILL_ALIASES.get(
        normalized,
        normalized,
    )


def unique_skills(skills: list[str]) -> list[str]:
    """Remove duplicate skills while preserving readable names."""

    seen = set()
    result = []

    for skill in skills:
        cleaned_skill = skill.strip()

        if not cleaned_skill:
            continue

        normalized = normalize_skill(cleaned_skill)

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(cleaned_skill)

    return result


def add_evidence(
    evidence_map: dict[str, list[str]],
    skill: str,
    evidence: str,
) -> None:
    """Add résumé evidence for a particular skill."""

    normalized = normalize_skill(skill)

    if not normalized:
        return

    if evidence not in evidence_map[normalized]:
        evidence_map[normalized].append(evidence)


def build_direct_skill_evidence(
    profile: CandidateProfile,
) -> dict[str, list[str]]:
    """Collect direct skill evidence from résumé sections."""

    evidence_map: dict[str, list[str]] = defaultdict(list)

    for skill in profile.programming_languages:
        add_evidence(
            evidence_map,
            skill,
            f"Listed as programming language: {skill}",
        )

    for skill in profile.technical_skills:
        add_evidence(
            evidence_map,
            skill,
            f"Listed as technical skill: {skill}",
        )

    for skill in profile.tools:
        add_evidence(
            evidence_map,
            skill,
            f"Listed as tool: {skill}",
        )

    for skill in profile.soft_skills:
        add_evidence(
            evidence_map,
            skill,
            f"Listed as soft skill: {skill}",
        )

    for project in profile.projects:
        project_name = project.name or "Unnamed project"

        for technology in project.technologies:
            add_evidence(
                evidence_map,
                technology,
                (
                    f"Used in project '{project_name}': "
                    f"{technology}"
                ),
            )

    for experience in profile.experience:
        role = experience.role or "Work experience"

        for technology in experience.technologies:
            add_evidence(
                evidence_map,
                technology,
                (
                    f"Used during '{role}' experience: "
                    f"{technology}"
                ),
            )

    return evidence_map


def build_supporting_text_sources(
    profile: CandidateProfile,
) -> list[tuple[str, str]]:
    """Create text sources for partial evidence detection."""

    sources: list[tuple[str, str]] = []

    if profile.professional_summary:
        sources.append(
            (
                "Professional summary",
                profile.professional_summary,
            )
        )

    for project in profile.projects:
        project_name = project.name or "Unnamed project"

        project_text = " ".join(
            [
                project.description,
                " ".join(project.features),
            ]
        ).strip()

        if project_text:
            sources.append(
                (
                    f"Project description: {project_name}",
                    project_text,
                )
            )

    for experience in profile.experience:
        role = experience.role or "Work experience"

        experience_text = " ".join(
            experience.responsibilities
        ).strip()

        if experience_text:
            sources.append(
                (
                    f"Experience description: {role}",
                    experience_text,
                )
            )

    for course in profile.courses:
        sources.append(
            (
                "Course listed in résumé",
                course,
            )
        )

    for certification in profile.certifications:
        certification_text = " ".join(
            [
                certification.name,
                certification.issuer,
            ]
        ).strip()

        if certification_text:
            sources.append(
                (
                    "Certification listed in résumé",
                    certification_text,
                )
            )

    return sources


def get_search_patterns(skill: str) -> list[str]:
    """Return the canonical name and aliases for a skill."""

    normalized_skill = normalize_skill(skill)

    patterns = {
        basic_normalize(skill),
        normalized_skill,
    }

    for alias, canonical in SKILL_ALIASES.items():
        if canonical == normalized_skill:
            patterns.add(alias)

    return [
        pattern
        for pattern in patterns
        if pattern
    ]


def text_contains_skill(
    skill: str,
    text: str,
) -> bool:
    """Check whether a résumé description mentions a skill."""

    normalized_text = basic_normalize(text)
    padded_text = f" {normalized_text} "

    for pattern in get_search_patterns(skill):
        padded_pattern = f" {pattern} "

        if padded_pattern in padded_text:
            return True

    required_tokens = set(
        normalize_skill(skill).split()
    )

    text_tokens = set(
        normalized_text.split()
    )

    if (
        len(required_tokens) > 1
        and required_tokens.issubset(text_tokens)
    ):
        return True

    return False


def find_partial_evidence(
    skill: str,
    sources: list[tuple[str, str]],
) -> list[str]:
    """Find indirect evidence for a job-required skill."""

    evidence = []

    for source_name, source_text in sources:
        if text_contains_skill(skill, source_text):
            evidence.append(
                f"Mentioned in {source_name}"
            )

    return evidence


def build_required_skills(
    job: JobAnalysis,
) -> list[str]:
    """Combine all required job-related skill groups."""

    return unique_skills(
        [
            *job.required_skills,
            *job.programming_languages,
            *job.frameworks,
            *job.tools,
            *job.databases,
            *job.cloud_platforms,
            *job.knowledge_areas,
        ]
    )


def calculate_job_match(
    profile: CandidateProfile,
    job: JobAnalysis,
) -> JobMatchResult:
    """Compare candidate profile skills with target job skills."""

    required_skills = build_required_skills(job)

    preferred_skills = unique_skills(
        job.preferred_skills
    )

    direct_evidence = build_direct_skill_evidence(
        profile
    )

    supporting_sources = build_supporting_text_sources(
        profile
    )

    matching_skills: list[SkillMatchItem] = []
    partially_evidenced: list[SkillMatchItem] = []
    missing_skills: list[str] = []

    for skill in required_skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in direct_evidence:
            matching_skills.append(
                SkillMatchItem(
                    skill=skill,
                    evidence=direct_evidence[
                        normalized_skill
                    ],
                )
            )

            continue

        partial_evidence = find_partial_evidence(
            skill,
            supporting_sources,
        )

        if partial_evidence:
            partially_evidenced.append(
                SkillMatchItem(
                    skill=skill,
                    evidence=partial_evidence,
                )
            )

            continue

        missing_skills.append(skill)

    matched_preferred = []
    missing_preferred = []

    for skill in preferred_skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in direct_evidence:
            matched_preferred.append(skill)
            continue

        partial_evidence = find_partial_evidence(
            skill,
            supporting_sources,
        )

        if partial_evidence:
            matched_preferred.append(skill)
        else:
            missing_preferred.append(skill)

    required_total = len(required_skills)

    required_points = (
        len(matching_skills)
        + (0.5 * len(partially_evidenced))
    )

    required_ratio = (
        required_points / required_total
        if required_total
        else 0
    )

    preferred_total = len(preferred_skills)

    preferred_ratio = (
        len(matched_preferred) / preferred_total
        if preferred_total
        else 0
    )

    if preferred_total:
        match_percentage = round(
            (required_ratio * 85)
            + (preferred_ratio * 15)
        )
    else:
        match_percentage = round(
            required_ratio * 100
        )

    match_percentage = max(
        0,
        min(match_percentage, 100),
    )

    strengths = [
        f"Strong evidence for {item.skill}"
        for item in matching_skills[:5]
    ]

    next_steps = [
        (
            f"Verify your knowledge of {skill} "
            "or begin the recommended course."
        )
        for skill in missing_skills[:5]
    ]

    next_steps.extend(
        [
            (
                "Add stronger project or experience evidence "
                f"for {item.skill}."
            )
            for item in partially_evidenced[:3]
        ]
    )

    if not required_skills:
        next_steps.append(
            "The job description did not contain enough "
            "clear technical requirements."
        )

    return JobMatchResult(
        target_role=job.target_role,
        match_percentage=match_percentage,
        required_skill_count=len(required_skills),
        preferred_skill_count=len(preferred_skills),
        matched_count=len(matching_skills),
        partial_count=len(partially_evidenced),
        missing_count=len(missing_skills),
        matching_skills=matching_skills,
        partially_evidenced_skills=partially_evidenced,
        missing_skills=missing_skills,
        matched_preferred_skills=matched_preferred,
        missing_preferred_skills=missing_preferred,
        strengths=strengths,
        next_steps=next_steps,
    )