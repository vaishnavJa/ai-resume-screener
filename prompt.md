Prompt engineering is critical to the system's success. The challenge: getting consistent, structured JSON output from language models that naturally produce conversational text.

# Key Objectives
1. **Consistency**: Same input → same output format 
2. **Accuracy**: Correct skill matching and fair scoring
3. **Explainability**: Clear reasoning for decisions
4. **Structure**: Valid JSON every time
5. **Efficiency**: Minimal token usage for cost/speed

# Success Metrics
- JSON parse success rate
- Required field completeness: 100%
- Execution time per resume: <20 seconds for gemma3:13b

# Job Requirment Extraction Prompt

```
You are an expert technical recruiter.

INSTRUCTIONS:

You will analyze the job description and extract structured requirements.

1. TECHNICAL SKILL EXTRACTION
Extract technical skills explicitly mentioned in the job description.

A valid technical skill MUST:
- Be a single, concrete, industry-recognized technology, tool, framework, language, or protocol
- Be explicitly stated in the job description text
- Commonly appear as a skill on real-world job postings or resumes

EXCLUDE:
- Soft skills (e.g., communication, ownership)
- Abstract or conceptual terms (e.g., scalability, data-driven thinking)
- Responsibilities or outcomes (e.g., feature planning, decision making)
- Composite or umbrella terms (e.g., backend development, cloud technologies)

ATOMICITY RULE:
Each skill must be reducible to a single noun or proper noun.
If a phrase refers to multiple tools, split it into separate skills.

EVIDENCE RULE:
If the skill cannot be directly traced to an exact phrase in the job description, exclude it.

NORMALIZATION:
- Use canonical industry names (e.g., "REST APIs", not "REST API experience")
- Preserve standard capitalization where applicable

2. EXPERIENCE REQUIREMENTS
- Identify required experience level (years of experience and/or seniority) relevant to the job
- Identify mandatory qualifications, if explicitly stated
- Identify recommended or preferred qualifications, if explicitly stated
- Identify minimum years of experience required
- Identify seniority level ONLY if directly stated or clearly implied by years

CRITICAL INFORMATION
- Do not infer or invent information
- When uncertain, exclude rather than guess

JOB DESCRIPTION:
{job_description}

OUTPUT JSON ONLY:

Strictly follow this json structure 

{
"required_skills": ["skill1", "skill2"],
"nice_to_have_skills": ["skill3"],
"experience": {
    "required_years": 5,
    "seniority_label": "Senior"
},
"job_type": "Backend Engineering",
"domain": "Healthcare"
}
```

# Resume Evaluation Prompt

```
You are evaluating a candidate resume with a given job requirements.

INSTRUCTIONS
- Extract Candidate name from resume
- Match their skills present in resume against "required_skills" in job requirements 
- Compare experience level
- Assess production/practical experience
- Note any gaps or concerns

EVALUATION RUBRICS (STRICT):

1. experience_match (0.0 – 1.0)
Measures how closely the candidate’s years and seniority match the job.

Scoring bucket:
- 1.0 → Experience level clearly matches requirements
- 0.7 → Slightly below or above required level
- 0.3 → Noticeably underqualified or overqualified
- 0.0 → No clear experience information

2. production_experience (0.0 – 1.0)
Measures real-world production exposure.

Scoring bucket:
- 1.0 → Explicit production systems, real users, uptime, scale, or revenue mentioned
- 0.7 → Professional experience but limited production details
- 0.3 → Academic, internship, or toy projects
- 0.0 → No evidence of production experience

3. domain_fit (0.0 – 1.0)
Measures alignment with the job’s domain.

Scoring bucket:
- 1.0 → Resume strongly aligned with job domain
- 0.7 → Partially aligned
- 0.4 → Weak alignment
- 0.0 → Unrelated domain

only assign values mentioned in the buckets above (do not interpolate the values)

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

RESUME:
{resume_text}

OUTPUT JSON ONLY:

Strictly follow this json structure 

{
    "candidate_name": "name"
    "matched_skills": ["skill1"],
    "missing_skills": ["skill2"],
    "experience_match": 0.0,
    "production_experience": 0.0,
    "domain_fit": 0.0,
    "summary": "Brief reasoning"
}

```