# AI Resume Screening System

An intelligent resume screening system that uses local LLMs (via Ollama) to evaluate candidates against job descriptions. Built for efficient, consistent, and unbiased candidate evaluation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Ollama](https://img.shields.io/badge/ollama-local-green.svg)


## Features

- **AI-Powered Evaluation**: Uses local LLMs (Gemma, Llama, Qwen) for resume analysis
- **Comprehensive Scoring**: Multi-factor evaluation (skills, experience, production expertise, domain fit)
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Detailed Reports**: Skills matching, explanations, and recommendations
- **Export Options**: JSON and detailed text reports
- **Privacy-First**: 100% local processing, no data leaves your machine

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: ~15GB for models
- **OS**: Windows, macOS, or Linux

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vaishnavJa/ai-resume-screener.git
cd ai-resume-screener
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

**Windows/Mac:**
- Download from [ollama.ai/download](https://ollama.ai/download)
- Run the installer

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 5. Download AI Models

```bash
# In a new terminal, pull models (choose one or more)
ollama pull gemma3:12b      # Recommended - balanced
ollama pull gemma3:27b     # Better quality, needs more RAM
ollama pull qwen3:8b     # Alternative

# Start Ollama service
ollama serve

```

to use a new ollam model

```bash
ollama pull <model>
```

## 📁 Project Structure

```
ai-resume-screener/
├── src
│  ├── app.py                      # Streamlit frontend
│  ├── resume_evaluator.py         # Core evaluation logic
│  ├── main.py                     # evaluation in CLI
│  └── utils.py                    # Utility functions
├── dataset/
│   ├──data1       
│   │  ├── JD.txt                  # Sample job description
│   │  └── resumes/                # Sample resumes
│   │      ├── resume_001.txt
│   │      ├── resume_002.txt
│   │      └── ...
│   └──data2       
│       ├── JD.txt
│       └─ ...
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore file
│
└──prompt.md   # Prompt design documentation

```

## Usage

```bash

# FOR front-end solution
streamlit run ai-resume-screener/src/app.py

# For CLI 
python src\main.py --model-name gemma3:12b 
  --debug_mode True 
  --job_description_path dataset\data1\JD.txt 
  --resume_folder_path dataset\data1\resume
```

Then open your browser to `http://localhost:8501`

**Steps:**
1. Enter or upload job description
2. Upload resume files (.txt format)
3. Select AI model
4. Click "Evaluate Resumes"
5. View results and export reports



## 📊 Sample Output

```json
{
  "job_requirements": {
    "required_skills": [
      "PostgreSQL",
      "Backend Architecture",
      "API Development",
      "Production Deployment & Monitoring",
      "Supabase"
    ],
    "experience_level": "Senior"
  },
  "candidates": [
    {
      "candidate_file": "John Martinez",
      "file_name": "resume_001.txt",
      "fit_score": 0.88,
      "matched_skills": ["PostgreSQL", "API Development", "Supabase"],
      "missing_skills": [],
      "explanation": "Strong candidate with all required skills...",
      "recommendation": "Shortlist"
    }
  ]
}
```

## 🎯 Evaluation Methodology

The system uses a weighted scoring algorithm:

- **Technical Skills Match**: 40%
- **Experience Level**: 30%
- **Production Experience**: 20%
- **Domain Fit**: 10%

**Recommendations:**
- **Shortlist**: Fit score ≥ 0.75 (Strong match)
- **Review**: Fit score 0.50-0.74 (Potential fit)
- **Reject**: Fit score < 0.50 (Poor match)



## 🔧 Configuration

### Scoring Weights

Modify in `resume_evaluator.py`:

```python
def calculate_fit_score(self, skill_match, exp_match, prod_exp, domain_fit):
    return (
        skill_match * 0.4 +    # Skills: 40%
        exp_match * 0.3 +      # Experience: 30%
        prod_exp * 0.2 +       # Production: 20%
        domain_fit * 0.1       # Domain: 10%
    )

def get_recommendation(self, score: float) -> str:
        if score >= 0.75:
            return "Shortlist"
        elif score >= 0.50:
            return "Review"
        return "Reject"
```



## 🛠️ Troubleshooting

### Issue: "Connection refused to Ollama"

```bash
# Make sure Ollama is running
ollama serve

# Test with
ollama run gemma3:12b "Hello"
```

### Issue: "Out of memory"

- Use smaller models: `gemma2:9b` or `llama3.2:3b`
- Close other applications
- Reduce batch size

### Issue: "Model not found"

```bash
# List available models
ollama list

# Pull missing model
ollama pull gemma3:27b
```

### Issue: "Invalid JSON response"

- Lower temperature in prompt (already set to 0.1-0.2)
- Try different model
- Check debug output in console

## 🎨 Customization


### Custom Scoring Logic

Modify `calculate_fit_score()` in `resume_evaluator.py`

## 📝 Dataset Format

### Job Description (.txt)
Plain text file with job requirements, responsibilities, and qualifications.

### Resumes (.txt)
Plain text format. The system extracts:
- Candidate name (from header)
- Skills and technologies
- Experience duration

There are example samples in `dataset` folder
