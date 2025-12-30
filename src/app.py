"""
Integration module for connecting Streamlit frontend with your backend
Place this in the same directory as your main.py
"""

import streamlit as st
import json
import time
from pathlib import Path
import tempfile
import os

# Import your existing modules
from utils import read_file, get_available_ollama_models
from resume_evaluator import ResumeEvaluator

# Page configuration
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .candidate-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 2px solid;
    }
    .shortlist-card {
        background-color: #f0fdf4;
        border-color: #22c55e;
    }
    .review-card {
        background-color: #fefce8;
        border-color: #eab308;
    }
    .reject-card {
        background-color: #fef2f2;
        border-color: #ef4444;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .matched-skill {
        background-color: #dcfce7;
        color: #166534;
    }
    .missing-skill {
        background-color: #fee2e2;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

def evaluate_resumes_backend(job_description, resume_files_data, model_name, progress_bar, status_text, debug=False):
    """
    Wrapper function to call your existing backend
    """
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save resumes to temp files
        resume_paths = []
        for idx, resume_data in enumerate(resume_files_data):
            temp_path = os.path.join(temp_dir, resume_data['name'])
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(resume_data['content'])
            resume_paths.append(temp_path)
        
        # Initialize evaluator
        output_path = "outputs" if debug else temp_dir
        os.makedirs(output_path, exist_ok=True)
        
        evaluator = ResumeEvaluator(
            output_path=output_path,
            model_name=model_name,
            debug_mode=debug
        )
        
        # Extract job requirements

        status_text.text("Extracting job requirements...")
        progress_bar.progress(20)

        job_requirements = evaluator.extract_job_requirements(job_description)
        
        total_resumes = len(resume_paths)
        results = []
        
        # Process each resume
        for idx, resume_path in enumerate(resume_paths):

            status_text.text(f"Processing Resume({idx+1}/{total_resumes}) ")
            progress_bar.progress(min(100 , 20 + int((idx+1)/total_resumes * 80) ))
            resume_text = read_file(resume_path)
            
            # Analyze resume
            analysis = evaluator.analyze_single_resume(
                job_requirements, 
                resume_text, 
                idx+1
            )
            
            # Calculate fit score
            skill_match_ratio = (
                len(analysis["matched_skills"]) /
                max(len(job_requirements["required_skills"]), 1)
            )
            
            fit_score = evaluator.calculate_fit_score(
                skill_match_ratio,
                analysis["experience_match"],
                analysis["production_experience"],
                analysis["domain_fit"]
            )
            
            # Build result
            result = {
                "candidate_file": analysis["candidate_name"],
                "file_name": os.path.basename(resume_path),
                "fit_score": fit_score,
                "matched_skills": analysis["matched_skills"],
                "missing_skills": analysis["missing_skills"],
                "experience_match": analysis["experience_match"],
                "production_experience": analysis["production_experience"],
                "domain_fit": analysis["domain_fit"],
                "explanation": analysis["summary"],
                "recommendation": evaluator.get_recommendation(fit_score)
            }
            
            results.append(result)
        
        # Return complete evaluation
        evaluation = {
            "job_requirements": job_requirements,
            "candidates": sorted(results, key=lambda x: x["fit_score"], reverse=True)
        }
        
        return evaluation

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'evaluation_done' not in st.session_state:
    st.session_state.evaluation_done = False

if 'available_models' not in st.session_state:
    st.session_state.available_models = get_available_ollama_models()

# Header
st.markdown('<div class="main-header">💼 AI Resume Screener</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Evaluate candidates efficiently with AI-powered analysis</div>', unsafe_allow_html=True)

# Sidebar - Input Section
with st.sidebar:
    st.header("📋 Configuration")
    
    # Model Selection
    st.subheader("Select Model")
    if len(st.session_state.available_models) < 1:
        st.error("⚠️ download a model using ollama pull <model>")
    selected_model = st.selectbox(
        "Choose AI Model",
        st.session_state.available_models,
        index=1,
        help="Select the language model for evaluation"
    )
    
    # Debug mode
    debug_mode = st.checkbox("Enable Debug Mode", value=False, help="Save detailed outputs")
    
    st.divider()
    
    # Job Description Input
    st.subheader("📄 Job Description")
    
    job_desc_option = st.radio(
        "Input Method",
        ["Type/Paste", "Upload File"],
        horizontal=True
    )
    
    job_description = ""
    
    if job_desc_option == "Upload File":
        jd_file = st.file_uploader(
            "Upload Job Description (.txt)",
            type=['txt'],
            key='jd_upload'
        )
        if jd_file:
            job_description = jd_file.read().decode('utf-8')
            st.success(f"✅ Loaded: {jd_file.name}")
            with st.expander("Preview"):
                st.text(job_description[:300] + "...")
    else:
        job_description = st.text_area(
            "Enter Job Description",
            height=200,
            placeholder="Paste the job description here..."
        )
    
    st.divider()
     
    # Resume Upload
    st.subheader("📁 Upload Resumes")
    resume_files = st.file_uploader(
        "Upload Resume Files (.txt)",
        type=['txt'],
        accept_multiple_files=True,
        key='resume_upload',
        help="Select multiple resume files to evaluate"
    )
    
    if resume_files:
        st.info(f"{len(resume_files)} resume(s) uploaded")
        with st.expander("View uploaded files"):
            for i, file in enumerate(resume_files, 1):
                st.text(f"{i}. {file.name}")
    
    st.divider()
    
    # Evaluate Button
    evaluate_button = st.button(
        "Evaluate Resumes",
        type="primary",
        use_container_width=True,
        disabled=not (job_description and resume_files)
    )

# Main Content Area
if evaluate_button:
    if not job_description.strip():
        st.error("⚠️ Please provide a job description")
    elif not resume_files:
        st.error("⚠️ Please upload at least one resume")
    else:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        
        
        try:
            # Prepare resume data
            resume_files_data = []
            for resume_file in resume_files:
                resume_content = resume_file.read().decode('utf-8')
                resume_files_data.append({
                    'name': resume_file.name,
                    'content': resume_content
                })
            
            # progress_bar.progress(40)
            # status_text.text(f"🤖 Running AI evaluation with {selected_model}...")
            
            # Call your backend

            start = time.time()

            results = evaluate_resumes_backend(
                job_description,
                resume_files_data,
                selected_model,
                debug=debug_mode,
                progress_bar = progress_bar,
                status_text = status_text

            )

            print('duration : ', time.time() - start)
            
            st.session_state.results = results
            st.session_state.evaluation_done = True
            
            progress_bar.progress(100)
            status_text.text("✅ Evaluation complete!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"Successfully evaluated {len(results['candidates'])} candidates!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during evaluation: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
            progress_bar.empty()
            status_text.empty()

# Display Results
if st.session_state.evaluation_done and st.session_state.results:
    results = st.session_state.results
    
    # Summary Statistics
    st.header("Evaluation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    shortlisted = len([c for c in results['candidates'] if c['recommendation'] == 'Shortlist'])
    review = len([c for c in results['candidates'] if c['recommendation'] == 'Review'])
    rejected = len([c for c in results['candidates'] if c['recommendation'] == 'Reject'])
    total = len(results['candidates'])
    
    with col1:
        st.metric("Total Candidates", total)
    with col2:
        st.metric("✅ Shortlisted", shortlisted, delta_color="normal")
    with col3:
        st.metric("🟡 Review", review, delta_color="off")
    with col4:
        st.metric("❌ Rejected", rejected, delta_color="inverse")
    
    st.divider()
    
    # Job Requirements
    with st.expander("📋 Job Requirements Analysis", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Required Skills")
            for skill in results['job_requirements']['required_skills']:
                st.markdown(f"- {skill}")
        
        with col2:
            if results['job_requirements'].get('nice_to_have_skills'):
                st.subheader("Nice to Have")
                for skill in results['job_requirements']['nice_to_have_skills']:
                    st.markdown(f"- {skill}")
        
        st.text(f"Experience Level: {results['job_requirements'].get('experience_level', 'N/A')}")
        st.text(f"Job Type: {results['job_requirements'].get('job_type', 'N/A')}")
        if results['job_requirements'].get('domain'):
            st.text(f"Domain: {results['job_requirements']['domain']}")
    
    st.divider()
    
    # Candidates List
    st.header("👥 Candidate Evaluations")
    
    # Filter options
    col1, col2 = st.columns([1, 3])
    with col1:
        filter_option = st.selectbox(
            "Filter by",
            ["All", "Shortlist", "Review", "Reject"]
        )
    with col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Fit Score (High to Low)", "Fit Score (Low to High)", "Name (A-Z)", "Name (Z-A)"]
        )
    
    filtered_candidates = results['candidates']
    if filter_option != "All":
        filtered_candidates = [c for c in results['candidates'] if c['recommendation'] == filter_option]
    
    # Apply sorting
    if sort_option == "Fit Score (High to Low)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: x['fit_score'], reverse=True)
    elif sort_option == "Fit Score (Low to High)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: x['fit_score'])
    elif sort_option == "Name (A-Z)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: x['candidate_file'])
    else:
        filtered_candidates = sorted(filtered_candidates, key=lambda x: x['candidate_file'], reverse=True)
    
    # Display candidates
    for idx, candidate in enumerate(filtered_candidates, 1):
        recommendation = candidate['recommendation']
        
        # Determine card styling
        if recommendation == "Shortlist":
            card_class = "shortlist-card"
            icon = "✅"
            color = "#22c55e"
        elif recommendation == "Review":
            card_class = "review-card"
            icon = "🟡"
            color = "#eab308"
        else:
            card_class = "reject-card"
            icon = "❌"
            color = "#ef4444"
        
        # Candidate card
        with st.container():
            st.markdown(f'<div class="candidate-card {card_class}">', unsafe_allow_html=True)
            
            # Header row
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(f"{icon} {candidate['candidate_file']}")
                st.caption(f"📄 {candidate['file_name']}")
            
            with col2:
                st.markdown("**Fit Score**")
                st.markdown(f"<h2 style='color: {color}; margin: 0;'>{candidate['fit_score']:.2f}</h2>", 
                           unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Recommendation**")
                st.markdown(f"<h3 style='color: {color}; margin: 0;'>{recommendation}</h3>", 
                           unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Expandable details
            with st.expander(f"📋 View Details - {candidate['candidate_file']}", expanded=False):
                # Explanation
                st.markdown("### 📝 Evaluation Summary")
                st.write(candidate['explanation'])
                st.divider()
                
                # Skills comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Matched Skills")
                    if candidate['matched_skills']:
                        skills_html = ""
                        for skill in candidate['matched_skills']:
                            skills_html += f'<span class="skill-badge matched-skill">{skill}</span>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.info("No matching skills found")
                
                with col2:
                    st.markdown("### ❌ Missing Skills")
                    if candidate['missing_skills']:
                        skills_html = ""
                        for skill in candidate['missing_skills']:
                            skills_html += f'<span class="skill-badge missing-skill">{skill}</span>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.success("All required skills present!")
                
                st.divider()
                
                # Additional metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    skill_match_percent = (len(candidate['matched_skills']) / 
                                          len(results['job_requirements']["required_skills"])) * 100
                    st.metric("Skill Match", f"{skill_match_percent:.0f}%")
                
                with col2:
                    st.metric("Matched Skills", len(candidate['matched_skills']))
                
                with col3:
                    st.metric("Missing Skills", len(candidate['missing_skills']))
                
                with col4:
                    st.metric("Experience Fit", candidate['experience_match'])

        
        st.markdown("<br>", unsafe_allow_html=True)
    
    if len(filtered_candidates) == 0:
        st.info(f"No candidates with '{filter_option}' recommendation")
    
    # Export Results
    st.divider()
    st.header("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download JSON
        json_str = json.dumps(results, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"evaluation_results{time.strftime('%Y-%m-%d %H:%M:%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Generate detailed report
        summary_text = f"""CANDIDATE EVALUATION REPORT
{'='*70}

Model Used: {selected_model}
Evaluation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY STATISTICS:
- Total Candidates: {total}
- Shortlisted: {shortlisted}
- Review: {review}
- Rejected: {rejected}

{'='*70}

JOB REQUIREMENTS:
Required Skills: {', '.join(results['job_requirements']['required_skills'])}
Experience Level: {results['job_requirements'].get('experience_level', 'N/A')}
Job Type: {results['job_requirements'].get('job_type', 'N/A')}

{'='*70}
CANDIDATE RANKINGS:

        """

        for idx, candidate in enumerate(results['candidates'], 1):
            summary_text += f"""
RANK #{idx}: {candidate['candidate_file']}
{'-'*70}
File: {candidate['file_name']}
Fit Score: {candidate['fit_score']:.2f}
Recommendation: {candidate['recommendation']}

Matched Skills ({len(candidate['matched_skills'])}):
{', '.join(candidate['matched_skills']) if candidate['matched_skills'] else 'None'}

Missing Skills ({len(candidate['missing_skills'])}):
{', '.join(candidate['missing_skills']) if candidate['missing_skills'] else 'None'}

Evaluation:
{candidate['explanation']}

{'='*70}
        """
        
        st.download_button(
            label="📄 Download Report",
            data=summary_text,
            file_name=f"evaluation_report{time.strftime('%Y-%m-%d %H:%M:%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Reset button
    if st.button("🔄 Start New Evaluation", type="secondary", use_container_width=True):
        st.session_state.results = None
        st.session_state.evaluation_done = False
        st.rerun()

else:
    # Welcome screen
    st.info("""
    **Welcome to AI Resume Screener!**
    
    Get started by:
    1. Entering or uploading a job description (left sidebar)
    2. Uploading resume files in .txt format
    3. Selecting your preferred AI model
    4. Clicking "Evaluate Resumes"
    
    The system will analyze each resume and provide:
    - Fit scores and recommendations
    - Matched vs missing skills
    - Detailed explanations
    - Hiring insights
    - Exportable results
    """)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Accurate Scoring
        AI-powered evaluation based on:
        - Technical skills match
        - Experience level
        - Production expertise
        - Domain fit
        """)
    
    with col2:
        st.markdown("""
        ### Fast Processing
        - Batch evaluation
        - Multiple models
        - Detailed analysis
        - Real-time results
        """)
    
    with col3:
        st.markdown("""
        ### Export Options
        - JSON format
        - CSV spreadsheet
        - Detailed report
        - Easy sharing
        """)