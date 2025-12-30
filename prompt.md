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
Extract structured hiring requirements from the job description below.
- Extract all atomic skills and tools from the resume
- An atomic skill is a single, concrete, industry-recognized technology, framework, language, or tool.
- Do NOT include abstract concepts, responsibilities, methodologies, or experience descriptions.
- Do NOT include composite or abstract terms
- Note required experience level (years, seniority)
- Identify mandatory qualifications
- Identify recommeneded qualifications

JOB DESCRIPTION:
{job_description}

OUTPUT JSON ONLY:
{{
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill3"],
    "experience_level": "Junior/Senior/Staff/Principal",
    "job_type": "Backend Engineering",
    "domain": "Healthcare"
}}
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
{{
    "candidate_name": "name"
    "matched_skills": ["skill1"],
    "missing_skills": ["skill2"],
    "experience_match": 0.0,
    "production_experience": 0.0,
    "domain_fit": 0.0,
    "summary": "Brief reasoning"
}}

```