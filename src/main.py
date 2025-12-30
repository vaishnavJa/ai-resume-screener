from utils import *
from resume_evaluator import ResumeEvaluator
import time
import glob
import os
from typing import List, Dict
import argparse


def evaluate_resumes(resumeEvaluator: ResumeEvaluator, job_description: str, resume_files: List[str]) -> Dict:

    job_requirements = resumeEvaluator.extract_job_requirements(job_description)
    results = []


    for id,resume_file in enumerate(resume_files):
        resume_text = read_file(resume_file)

        analysis = resumeEvaluator.analyze_single_resume(job_requirements, resume_text, id)

        skill_match_ratio = (
            len(analysis["matched_skills"]) /
            max(len(job_requirements["required_skills"]), 1)
        )

        fit_score = resumeEvaluator.calculate_fit_score(
            skill_match_ratio,
            analysis["experience_match"],
            analysis["production_experience"],
            analysis["domain_fit"]
        )

        result = {
            "candidate_file": analysis["candidate_name"],
            "file_name": os.path.basename(resume_file),
            "fit_score": fit_score,
            "matched_skills": analysis["matched_skills"],
            "missing_skills": analysis["missing_skills"],
            "experience_match": analysis["experience_match"],
            "production_experience": analysis["production_experience"],
            "domain_fit": analysis["domain_fit"],
            "explanation": analysis["summary"],
            "recommendation": resumeEvaluator.get_recommendation(fit_score)
        }

        results.append(result)

    return  {
        "job_requirements": job_requirements,
        "candidates": sorted(results, key=lambda x: x["fit_score"], reverse=True)
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="resume evaluation CLI")
    parser.add_argument("--model_name", type=str, default="gemma3:12b", help="downloaded model name from ollama")
    parser.add_argument("--debug_mode", type=bool, default=False, help="write intermidiate outputs in console for debug")
    parser.add_argument("--job_description_path", type=str, required=True, help="location of job descrption text file")
    parser.add_argument("--resume_folder_path", type=str, required=True, help="location of folder which contains all resumes to be evaluated, in text file")

    args = parser.parse_args()

    print("all args")
    for key,value in args.__dict__.items():
        print(f"{key}: {value}")

    start = time.time()

    job_description = read_file(args.job_description_path)
    resume_files = glob.glob(os.path.join(args.resume_folder_path,'*.txt'))

    if len(resume_files) < 1 or len(job_description) < 0:
        print('invalid or empty inputs, please check again')
        exit(0)

    os.makedirs('outputs',exist_ok=True)

    resumeEvaluator = ResumeEvaluator(output_path="outputs",model_name=args.model_name,debug_mode=args.debug_mode)
    evaluation = evaluate_resumes(resumeEvaluator, job_description, resume_files)

    write_json_output(os.path.join(resumeEvaluator.output_path,"evaluation_results.json"),evaluation)

    print("Evaluation completed in", round(time.time() - start, 2), "seconds")