import os
import subprocess
import shutil
import json
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import dotenv

dotenv.load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_branch(branch: str) -> str:
    if not branch:
        return "unknown"
    
    branch = branch.strip().lower()
    if (
        "cse" in branch
        or "computer science" in branch
        or "information technology" in branch
        or "electronics and computer" in branch
        or branch == "it"
        or "ai" in branch
        or "ml" in branch
        or "data science" in branch
    ):
        return "cse"
    elif "ece" in branch or "electronics and communication" in branch:
        return "ece"
    elif "mechanical" in branch:
        return "mechanical"
    elif "civil" in branch:
        return "civil"
    else:
        return "other"

def extract_resume_data(resume_content: str, form_data: dict):
    """Extract structured data from resume content using AI"""
    extraction_prompt = f"""
Extract ONLY these details from the resume text and return as JSON:

Resume: {resume_content}

JSON format:
{{
    "full_name": "ACTUAL name from resume",
    "email": "ACTUAL email from resume", 
    "phone": "ACTUAL phone from resume",
    "linkedin_url": "ACTUAL LinkedIn URL or https://linkedin.com/in/profile",
    "github_url": "ACTUAL GitHub URL or https://github.com/username",
    "address": "ACTUAL location from resume",
    "professional_summary": "Strong summary based on resume skills and experience",
    "institution_name": "ACTUAL college name from resume",
    "education_duration": "ACTUAL dates or 2022-{form_data.get('gradYear', '2026')}",
    "degree_program": "ACTUAL degree or B.Tech in {form_data.get('branch', 'Computer Science')}",
    "gpa_info": "CGPA: {form_data.get('cgpa', '8.0')}/10",
    "programming_languages": "ACTUAL languages from resume",
    "frameworks_libraries": "ACTUAL frameworks from resume", 
    "developer_tools": "ACTUAL tools from resume",
    "databases_apis": "ACTUAL databases from resume",
    "soft_skills": "ACTUAL soft skills from resume",
    "has_experience": true if internships/jobs found else false,
    "has_certifications": true if certifications found else false,
    "has_extracurricular": true if activities found else false,
    "experience": [{{
        "company_name": "Company name if found",
        "job_title": "Position title",
        "employment_duration": "Duration",
        "location": "Location",
        "responsibilities": ["Responsibility 1", "Responsibility 2"]
    }}],
    "certifications": [{{
        "name": "Certification name",
        "issuer": "Issuing organization",
        "date": "Date obtained"
    }}],
    "extracurricular_activities": ["Activity 1", "Achievement 2"],
    "projects": [{{
        "title": "ACTUAL project name",
        "date": "ACTUAL date or 2024",
        "live_demo_url": "ACTUAL URL or https://demo.com", 
        "github_url": "ACTUAL GitHub or https://github.com/user/repo",
        "bullets": ["ACTUAL description 1", "ACTUAL description 2"]
    }}]
}}"""
    
    try:
        completion = client.chat.completions.create(
            model="openrouter/sonoma-sky-alpha",  # FIXED: Removed :free
            messages=[
                {"role": "system", "content": "Extract ACTUAL data from resume. Return ONLY JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0,
            max_tokens=3000
        )
        
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            response = completion.choices[0].message.content.strip()
        else:
            print(f"❌ Unexpected completion format: {type(completion)}")
            return get_realistic_fallback(form_data, resume_content)
        
        # FIXED: Clean JSON response
        if "```":
            start = response.find('{')
            end = response.rfind('}') + 1
            response = response[start:end] if start != -1 and end > start else response
        elif "```" in response:
            start = response.find('{')
            end = response.rfind('}') + 1
            response = response[start:end] if start != -1 and end > start else response
        
        data = json.loads(response)
        print("✅ Real data extracted successfully")
        return data
        
    except Exception as e:
        print(f"❌ Using fallback due to: {e}")
        return get_realistic_fallback(form_data, resume_content)

def get_realistic_fallback(form_data, resume_content):
    """Generate realistic fallback data when JSON extraction fails"""
    lines = resume_content.split('\n')[:10]
    
    name = "Candidate Name"
    email = "candidate@email.com"
    
    for line in lines:
        line_clean = line.strip()
        # Skip empty lines and lines with common words
        if (len(line_clean.split()) <= 3 and 
            len(line_clean) > 5 and 
            any(c.isupper() for c in line_clean) and
            '@' not in line_clean and 
            'http' not in line_clean.lower() and
            not any(word in line_clean.lower() for word in ['email', 'phone', 'linkedin', 'github', 'address'])):
            name = line_clean
            break
            
        # Extract email
        if '@' in line_clean and '.' in line_clean and len(line_clean.split()) <= 1:
            email = line_clean.strip()
    
    return {
        "full_name": name,
        "email": email,
        "phone": "+91 9876543210",
        "linkedin_url": "https://linkedin.com/in/student",
        "github_url": "https://github.com/student",
        "portfolio_url": "https://portfolio.com", 
        "portfolio_name": "Portfolio",
        "address": "India",
        "professional_summary": f"Dedicated {form_data.get('branch', 'Engineering')} student with strong technical foundation and practical project experience.",
        "institution_name": "Engineering Institute",
        "education_duration": f"2022 – {form_data.get('gradYear', '2026')}",
        "degree_program": f"B.Tech in {form_data.get('branch', 'Computer Science')}",
        "gpa_info": f"CGPA: {form_data.get('cgpa', '8.0')}/10",
        "programming_languages": "Python, Java, JavaScript, C++",
        "frameworks_libraries": "Django, React.js, Spring Boot, Node.js",
        "developer_tools": "Git, VS Code, Docker, IntelliJ IDEA",
        "databases_apis": "MySQL, PostgreSQL, MongoDB, REST APIs",
        "soft_skills": "Problem Solving, Leadership, Team Collaboration, Communication",
        "has_experience": "internship" in resume_content.lower() or "intern" in resume_content.lower(),
        "has_certifications": "certification" in resume_content.lower() or "certified" in resume_content.lower(),
        "has_extracurricular": any(word in resume_content.lower() for word in ["sports", "volunteer", "competition", "fest", "club"]),
        "experience": [{
            "company_name": "Tech Company",
            "job_title": "Software Intern",
            "employment_duration": "June 2024 - August 2024",
            "location": "Remote",
            "responsibilities": ["Developed web applications", "Collaborated with senior developers"]
        }] if "internship" in resume_content.lower() else [],
        "certifications": [{
            "name": "Python Programming",
            "issuer": "Coursera",
            "date": "2024"
        }] if "certification" in resume_content.lower() else [],
        "extracurricular_activities": ["Technical club member", "Coding competition participant"] if any(word in resume_content.lower() for word in ["sports", "volunteer", "competition", "fest", "club"]) else [],
        "projects": [{
            "title": "Full Stack Development Project",
            "date": "2024",
            "live_demo_url": "https://project-demo.com",
            "github_url": "https://github.com/student/project",
            "bullets": [
                "Developed full-stack web application using modern frameworks",
                "Implemented user authentication and database integration", 
                "Deployed scalable solution with optimized performance"
            ]
        }]
    }

def populate_latex_template(template_path: str, data: dict, output_path: str):
    """Populate LaTeX template with extracted data - FIXED VERSION"""
    try:
        if not os.path.exists(template_path):
            print(f"❌ Template not found at: {template_path}")
            return False
            
        print(f"🔄 Reading template from: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        def escape_latex(text):
            if not isinstance(text, str):
                text = str(text)
            replacements = {
                '&': '\\&', '%': '\\%', '$': '\\$', '#': '\\#',
                '_': '\\_', '{': '\\{', '}': '\\}',
                '~': '\\textasciitilde{}', '^': '\\textasciicircum{}'
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Fix URLs
        def fix_url(url):
            if not url or url == '#' or url.strip() == '':
                return 'https://linkedin.com/in/profile'
            return url.strip()
        
        # Clean all string data
        clean_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                clean_data[key] = escape_latex(value)
            else:
                clean_data[key] = value
        
        # Fix URLs
        clean_data['linkedin_url'] = fix_url(clean_data.get('linkedin_url', ''))
        clean_data['github_url'] = fix_url(clean_data.get('github_url', ''))
        
        # Replace simple template variables
        for key, value in clean_data.items():
            if isinstance(value, str):
                placeholder = f"{{{{{key}}}}}"
                template_content = template_content.replace(placeholder, value)
                print(f"✅ Replaced {key}")
        
        # FIXED: Handle projects section properly - NO DUPLICATION
        projects_latex = ""
        if 'projects' in data and data['projects']:
            for i, project in enumerate(data['projects']):
                project_title = escape_latex(str(project.get('title', f'Project {i+1}')))
                project_date = escape_latex(str(project.get('date', '2024')))
                
                project_latex = f"""
      \\resumeProjectHeading
          {{\\textbf{{{project_title}}}}}{{{project_date}}}
          \\resumeItemListStart"""
                
                bullets = project.get('bullets', [])
                for bullet in bullets[:3]:  # Limit to 3 bullets
                    if bullet and str(bullet).strip():
                        escaped_bullet = escape_latex(str(bullet).strip())
                        project_latex += f"\n            \\resumeItem{{{escaped_bullet}}}"
                
                project_latex += "\n          \\resumeItemListEnd"
                projects_latex += project_latex
        
        template_content = template_content.replace('{{PROJECT_CONTENT}}', projects_latex)
        
        # FIXED: Handle experience section conditionally
        experience_section = ""
        if data.get('has_experience', False) and data.get('experience', []):
            experience_section = """
\\section{Experience}
  \\resumeSubHeadingListStart"""
            
            for exp in data.get('experience', []):
                exp_latex = f"""
    \\resumeSubheading
      {{{escape_latex(exp.get('company_name', 'Company'))}}}{{{escape_latex(exp.get('employment_duration', 'Duration'))}}}
      {{{escape_latex(exp.get('job_title', 'Position'))}}}{{{escape_latex(exp.get('location', 'Location'))}}}
      \\resumeItemListStart"""
                
                for resp in exp.get('responsibilities', [])[:3]:
                    if resp:
                        exp_latex += f"\n        \\resumeItem{{{escape_latex(str(resp))}}}"
                
                exp_latex += "\n      \\resumeItemListEnd"
                experience_section += exp_latex
            
            experience_section += "\n  \\resumeSubHeadingListEnd"
        
        template_content = template_content.replace('{{EXPERIENCE_SECTION}}', experience_section)
        
        # FIXED: Handle achievements section conditionally
        achievements_section = ""
        if data.get('has_extracurricular', False) and data.get('extracurricular_activities', []):
            achievements_section = """
\\section{Achievements \\& Activities}
\\resumeSubHeadingListStart
  \\resumeItemListStart"""
            
            for activity in data.get('extracurricular_activities', []):
                if activity:
                    achievements_section += f"\n    \\resumeItem{{{escape_latex(str(activity))}}}"
            
            achievements_section += "\n  \\resumeItemListEnd\n\\resumeSubHeadingListEnd"
        
        template_content = template_content.replace('{{ACHIEVEMENTS_SECTION}}', achievements_section)
        
        # Clean any remaining template syntax
        import re
        template_content = re.sub(r'\{\{[^}]+\}\}', '', template_content)
        
        # Write the populated template
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(template_content)
        
        print("✅ Template populated successfully - NO DUPLICATIONS")
        return True
        
    except Exception as e:
        print(f"❌ Template error: {e}")
        return False

def compile_latex_to_pdf(tex_file_path: str) -> str:
    """Compile LaTeX file to PDF using pdflatex"""
    try:
        tex_dir = os.path.dirname(os.path.abspath(tex_file_path))
        tex_filename = os.path.basename(tex_file_path)
        
        print(f"🔄 Compiling LaTeX in directory: {tex_dir}")
        print(f"🔄 File: {tex_filename}")
        
        for i in range(2):
            print(f"🔄 LaTeX compilation pass {i+1}")
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', tex_dir, tex_filename],
                cwd=tex_dir,
                capture_output=True, 
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"❌ LaTeX Error (Pass {i+1}): {result.stderr}")
                if i == 1:
                    print(f"❌ LaTeX Full Output: {result.stdout}")
                continue
        
        pdf_filename = tex_filename.replace('.tex', '.pdf')
        pdf_path = os.path.join(tex_dir, pdf_filename)
        
        if os.path.exists(pdf_path):
            print("✅ LaTeX compilation successful!")
            
            aux_extensions = ['.aux', '.log', '.out', '.fdb_latexmk', '.fls', '.synctex.gz']
            for ext in aux_extensions:
                aux_file = tex_filename.replace('.tex', ext)
                aux_path = os.path.join(tex_dir, aux_file)
                if os.path.exists(aux_path):
                    try:
                        os.remove(aux_path)
                    except:
                        pass
            
            return pdf_path
        else:
            print("❌ PDF file not created")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ LaTeX compilation timeout")
        return None
    except FileNotFoundError:
        print("❌ pdflatex not found. Please install LaTeX (MiKTeX/TeX Live)")
        return None
    except Exception as e:
        print(f"❌ LaTeX compilation error: {e}")
        return None

def save_simple_pdf(content: str, filename: str, title: str):
    """Fallback PDF generation"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import simpleSplit
        
        pdf_path = os.path.join(OUTPUT_DIR, filename)
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        y = height - 50
        margin = 50
        max_width = width - 2 * margin
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, title)
        y -= 40
        
        c.setFont("Helvetica", 11)
        
        for paragraph in content.split("\n"):
            if not paragraph.strip():
                y -= 15
                continue
                
            lines = simpleSplit(paragraph, "Helvetica", 11, max_width)
            
            for line in lines:
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 11)
                
                c.drawString(margin, y, line)
                y -= 15
        
        c.save()
        return pdf_path
    except Exception as e:
        print(f"❌ Simple PDF error: {e}")
        return None

def validate_and_enhance_questions(questions_content: str, candidate_branch: str, jd_content: str) -> str:
    """Validate and enhance interview questions if they're too short"""
    
    if len(questions_content) < 100:
        enhanced_questions = f"""Interview Questions:

1. Technical Skills: Explain how you would implement the main technologies mentioned in the job requirements using your {candidate_branch} background and current skill set.

2. Project Deep Dive: Walk me through your most complex project and explain how you would modify it to meet the specific requirements of this role.

3. Problem Solving: Describe your systematic approach to debugging and resolving complex technical issues in a production environment.

4. System Architecture: How would you design a scalable, maintainable solution for the type of applications this company builds?

5. Team Collaboration: Give a specific example of how you've successfully worked in a team to deliver a challenging technical project, including how you handled any conflicts or obstacles that arose."""
        
        return enhanced_questions
    
    return questions_content

@app.post("/generate")
async def generate_resume(
    resume: str = Form(...),
    jd: str = Form(...),
    tenth: str = Form(""),
    twelfth: str = Form(""),
    cgpa: str = Form(""),
    branch: str = Form(""),
    gap: str = Form(""),
    live: str = Form(""),
    dead: str = Form(""),
    experience: str = Form(""),
    gradYear: str = Form("")
):
    try:
        print("🚀 Starting resume generation...")
        
        # FIXED: Clean old PDFs - more comprehensive
        def cleanup_old_pdfs():
            old_files = [
                "ATS_Professional_Resume.pdf",
                "Professional_Resume.pdf",
                "Fallback_Resume.pdf", 
                "Updated_Resume.pdf",
                "resume.pdf"
            ]
            for filename in old_files:
                file_path = os.path.join(OUTPUT_DIR, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Cleaned up old file: {filename}")
                    except:
                        pass
        
        cleanup_old_pdfs()
        
        # AI processing for eligibility and tailoring
        candidate_branch_norm = normalize_branch(branch)
        jd_branch = ""
        jd_lower = jd.lower()
        if "branch:" in jd_lower:
            try:
                jd_branch = jd.split("Branch:")[1].split("\n")[0].strip()
            except:
                jd_branch = ""
        
        jd_branch_norm = normalize_branch(jd_branch)
        extra_info = f"""
Candidate Info: 10th: {tenth}%, 12th: {twelfth}%, CGPA: {cgpa}, Branch: {candidate_branch_norm}, Year: {gradYear}, Gap: {gap}, Live Backlogs: {live}, Dead Backlogs: {dead}, Experience: {experience} years
JD Branch: {jd_branch_norm}
"""

        # ENHANCED: Better prompt for interview questions
        prompt = f"""You are an expert ATS resume writer and technical interviewer.

**STRICT ELIGIBILITY CHECK:**
Candidate: CGPA {cgpa}, 10th: {tenth}%, 12th: {twelfth}%, Branch: {candidate_branch_norm}, Year: {gradYear}, Backlogs: {live} live/{dead} dead, Experience: {experience}y
JD Requirements: {jd_branch_norm} branch requirement

If ineligible, return ONLY: "INELIGIBLE: [specific criteria failed]"

**RESUME REWRITING REQUIREMENTS (if eligible):**
1. **Skills Mapping**: Transform candidate skills to match JD exactly
   - Java → Python, React → Angular, MySQL → PostgreSQL
   - Use JD keywords naturally throughout resume

2. **Project Enhancement**: Reframe projects with quantified impact
   - "Improved performance by X%", "Built system handling Y users"
   - Emphasize technologies mentioned in JD
   - NO duplication across sections

3. **ATS Optimization**: 
   - Use standard section headers: Summary, Education, Skills, Projects, Experience
   - Include relevant keywords from JD in appropriate sections
   - Quantify all achievements with numbers/metrics

4. **Professional Summary**: Write 3-4 lines highlighting JD-relevant skills and experience

5. **Section Organization**:
   - Projects go ONLY in Projects section
   - Work experience goes ONLY in Experience section  
   - Achievements go ONLY in Achievements section
   - NO content duplication between sections

**MANDATORY OUTPUT FORMAT:**
End response with exactly this structure:

---RESUME CONTENT ABOVE---

INTERVIEW QUESTIONS:
1. [Technical deep-dive question on primary JD technology with specific coding scenario]
2. [System design question combining candidate's project experience with JD architecture requirements]
3. [Complex debugging/problem-solving scenario relevant to JD tech stack]
4. [Scalability/performance question using JD technologies and frameworks]
5. [Behavioral leadership question: team conflict, project delivery, mentoring scenario]

**INPUT DATA:**
Candidate Resume: {resume}

Job Description: {jd}

Academic Details: {extra_info}

**INSTRUCTIONS:**
- Generate professional, ATS-optimized resume content
- Ensure each section has unique, non-duplicated content
- Create exactly 5 challenging, role-specific interview questions
- Use quantifiable achievements and JD keywords throughout
- Make content compelling and interview-ready

Generate the complete resume rewrite with exactly 5 detailed interview questions."""


        try:
            completion = client.chat.completions.create(
                model="openrouter/sonoma-sky-alpha",
                messages=[
                    {"role": "system", "content": "You are a resume assistant. You MUST end every response with exactly 5 numbered INTERVIEW QUESTIONS. This is mandatory."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                output = completion.choices[0].message.content
                print(f"✅ AI processing complete - {len(output)} characters")
                print(f"🔍 Raw output preview: {output[:200]}...")
            else:
                print(f"❌ Unexpected completion format: {type(completion)}")
                return JSONResponse({"error": "AI response failed"}, status_code=500)
                
        except Exception as api_error:
            print(f"💥 API Error: {api_error}")
            return JSONResponse({"error": f"API Error: {str(api_error)}"}, status_code=500)
        
        # Handle ineligibility
        if output.lower().startswith("ineligible") or "not eligible" in output.lower()[:200]:
            note_pdf = "Eligibility_Note.pdf"
            save_simple_pdf(output, note_pdf, "Eligibility Result")
            return JSONResponse({
                "resume_pdf_url": f"/download/{note_pdf}",
                "questions_pdf_url": None
            })

        # ENHANCED: Question extraction with better validation
        questions_content = ""
        separators = ["INTERVIEW QUESTIONS:", "Interview Questions:", "QUESTIONS:", "Questions:"]
        resume_part = output
        
        for separator in separators:
            if separator in output:
                parts = output.split(separator, 1)
                if len(parts) == 2:
                    resume_part = parts[0].strip()
                    questions_part = parts[1].strip()
                    
                    # Validate questions content length
                    if len(questions_part) > 100:
                        questions_content = f"Interview Questions:\n\n{questions_part}"
                        print(f"✅ Found {len(questions_part)} chars of questions using '{separator}'")
                    else:
                        print(f"⚠️ Questions too short: {len(questions_part)} chars")
                        questions_content = validate_and_enhance_questions("", candidate_branch_norm, jd)
                    break
        
        # Fallback if no questions found
        if not questions_content or len(questions_content) < 100:
            print("🔄 Using enhanced fallback questions")
            questions_content = validate_and_enhance_questions("", candidate_branch_norm, jd)
        
        print(f"📝 Resume part: {len(resume_part)} chars")
        print(f"❓ Final questions: {len(questions_content)} chars")

        # MAIN LATEX PIPELINE
        form_data = {
            'tenth': tenth, 'twelfth': twelfth, 'cgpa': cgpa, 
            'branch': branch, 'gradYear': gradYear
        }
        
        print("🔄 Step 1: Extracting structured data...")
        resume_data = extract_resume_data(resume_part, form_data)
        
        template_path = os.path.join(TEMPLATE_DIR, "main.tex")
        output_tex_path = os.path.join(OUTPUT_DIR, "resume.tex")
        
        print(f"🔄 Step 2: Template path: {template_path}")
        
        if populate_latex_template(template_path, resume_data, output_tex_path):
            print("🔄 Step 3: Compiling LaTeX...")
            
            pdf_path = None
            for attempt in range(3):
                print(f"🔄 LaTeX compilation attempt {attempt + 1}/3")
                pdf_path = compile_latex_to_pdf(output_tex_path)
                if pdf_path:
                    break
                elif attempt < 2:
                    print("⏳ Retrying in 1 second...")
                    import time
                    time.sleep(1)
            
            if pdf_path:
                # FIXED: Only create ONE resume file with consistent naming
                final_resume_name = "Professional_Resume.pdf"
                final_pdf_path = os.path.join(OUTPUT_DIR, final_resume_name)
                
                # Use move to avoid duplicates
                if os.path.exists(pdf_path):
                    shutil.move(pdf_path, final_pdf_path)
                
                # Generate questions PDF
                questions_pdf_name = "Interview_Questions.pdf"
                save_simple_pdf(questions_content, questions_pdf_name, "Technical Interview Questions")
                
                print("🎉 SUCCESS: Single professional resume generated!")
                print(f"📄 Resume: {final_resume_name}")
                print(f"❓ Questions: {questions_pdf_name}")
                
                return JSONResponse({
                    "resume_pdf_url": f"/download/{final_resume_name}",
                    "questions_pdf_url": f"/download/{questions_pdf_name}"
                })
            else:
                print("⚠️ LaTeX failed, using fallback...")
                resume_pdf_name = "Resume_Fallback.pdf"
                save_simple_pdf(resume_part.strip(), resume_pdf_name, "Updated Resume")
                questions_pdf_name = "Interview_Questions.pdf"
                save_simple_pdf(questions_content, questions_pdf_name, "Technical Interview Questions")
                
                return JSONResponse({
                    "resume_pdf_url": f"/download/{resume_pdf_name}", 
                    "questions_pdf_url": f"/download/{questions_pdf_name}"
                })
        else:
            return JSONResponse({"error": "Template population failed"}, status_code=500)
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    return JSONResponse({"error": "File not found"}, status_code=404)

# Serve frontend
app.mount("/static", StaticFiles(directory="front"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("front/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
