# Resume Builder (FastAPI + OpenRouter/OpenAI + LaTeX)

Lightweight resume rewriting and PDF generation service using FastAPI, an OpenRouter/OpenAI client, and a LaTeX template with a ReportLab fallback.

## Features
- AI-driven resume rewrite and ATS optimization.
- Extracts structured resume data using the AI client.
- Populates a LaTeX template and compiles it to PDF via `pdflatex`.
- Fallback PDF generation with ReportLab when LaTeX is unavailable.
- Serves a minimal frontend at `/` and raw static assets under `/static`.

## Quick start

Prerequisites:
- Python 3.8+
- LaTeX distribution with `pdflatex` (TeX Live / MiKTeX) for full pipeline
- An OpenRouter/OpenAI-compatible API key set as `OPENROUTER_API_KEY` in `.env`

Install dependencies:
```sh
pip install -r requirements.txt
```

Run the app:
```sh
# Option 1 (recommended)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Option 2
python app.py
```

Open http://localhost:8000 in your browser (serves [front/index.html](front/index.html)).

## API

POST /generate
- Form fields accepted: `resume`, `jd`, `tenth`, `twelfth`, `cgpa`, `branch`, `gap`, `live`, `dead`, `experience`, `gradYear`.
- Main handler: [`generate_resume`](app.py)

GET /download/{filename}
- Download generated PDFs.
- Handler: [`download_file`](app.py)

## Important implementation points (core functions)
- Branch normalization: [`normalize_branch`](app.py)
- Structured extraction (AI): [`extract_resume_data`](app.py)
- Fallback extraction: [`get_realistic_fallback`](app.py)
- Populate LaTeX template: [`populate_latex_template`](app.py)
- Compile LaTeX to PDF: [`compile_latex_to_pdf`](app.py)
- Simple PDF fallback (ReportLab): [`save_simple_pdf`](app.py)
- Interview question validation/enhancement: [`validate_and_enhance_questions`](app.py)

## Files & templates
- [app.py](app.py) — main FastAPI application and logic
- [requirements.txt](requirements.txt) — Python dependencies
- [.env](.env) — environment variables (not committed; create locally)
- [.gitignore](.gitignore)
- [templates/main.tex](templates/main.tex) — LaTeX resume template used by the pipeline
- [front/index.html](front/index.html) — minimal frontend served at `/`
- [front/output/resume.tex](front/output/resume.tex) — sample output TeX (frontend sample)
- [resume_env/pyvenv.cfg](resume_env/pyvenv.cfg) — local venv config (ignored via .gitignore)
- __pycache__/ — cached bytecode (ignored)

## Environment
Create a `.env` file with:
```
OPENROUTER_API_KEY=your_api_key_here
```

The app uses `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))` in [app.py](app.py).

## Notes & troubleshooting
- If `pdflatex` is not installed, the app falls back to a plain PDF generator using ReportLab (`save_simple_pdf`).
- Ensure your LaTeX template placeholders match keys produced by `extract_resume_data` and the cleanup code in [`populate_latex_template`](app.py).
- Check logs printed by the server for AI errors and LaTeX compilation details.

## File map (quick links)
- [app.py](app.py)
- [requirements.txt](requirements.txt)
- [.env](.env)
- [.gitignore](.gitignore)
- [templates/main.tex](templates/main.tex)
- [front/index.html](front/index.html)
- [front/output/resume.tex](front/output/resume.tex)
- [resume_env/pyvenv.cfg](resume_env/pyvenv.cfg)

---

If you want, I can:
- add a ready-to-use `.env.example`,
- add a small curl example for the `/generate` endpoint,
- or create a minimal GitHub Actions workflow to check install + lint.
```// filepath: README.md

# Resume Builder (FastAPI + OpenRouter/OpenAI + LaTeX)

Lightweight resume rewriting and PDF generation service using FastAPI, an OpenRouter/OpenAI client, and a LaTeX template with a ReportLab fallback.

## Features
- AI-driven resume rewrite and ATS optimization.
- Extracts structured resume data using the AI client.
- Populates a LaTeX template and compiles it to PDF via `pdflatex`.
- Fallback PDF generation with ReportLab when LaTeX is unavailable.
- Serves a minimal frontend at `/` and raw static assets under `/static`.

## Quick start

Prerequisites:
- Python 3.8+
- LaTeX distribution with `pdflatex` (TeX Live / MiKTeX) for full pipeline
- An OpenRouter/OpenAI-compatible API key set as `OPENROUTER_API_KEY` in `.env`

Install dependencies:
```sh
pip install -r requirements.txt
```

Run the app:
```sh
# Option 1 (recommended)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Option 2
python app.py
```

Open http://localhost:8000 in your browser (serves [front/index.html](front/index.html)).

## API

POST /generate
- Form fields accepted: `resume`, `jd`, `tenth`, `twelfth`, `cgpa`, `branch`, `gap`, `live`, `dead`, `experience`, `gradYear`.
- Main handler: [`generate_resume`](app.py)

GET /download/{filename}
- Download generated PDFs.
- Handler: [`download_file`](app.py)

## Important implementation points (core functions)
- Branch normalization: [`normalize_branch`](app.py)
- Structured extraction (AI): [`extract_resume_data`](app.py)
- Fallback extraction: [`get_realistic_fallback`](app.py)
- Populate LaTeX template: [`populate_latex_template`](app.py)
- Compile LaTeX to PDF: [`compile_latex_to_pdf`](app.py)
- Simple PDF fallback (ReportLab): [`save_simple_pdf`](app.py)
- Interview question validation/enhancement: [`validate_and_enhance_questions`](app.py)

## Files & templates
- [app.py](app.py) — main FastAPI application and logic
- [requirements.txt](requirements.txt) — Python dependencies
- [.env](.env) — environment variables (not committed; create locally)
- [.gitignore](.gitignore)
- [templates/main.tex](templates/main.tex) — LaTeX resume template used by the pipeline
- [front/index.html](front/index.html) — minimal frontend served at `/`
- [front/output/resume.tex](front/output/resume.tex) — sample output TeX (frontend sample)
- [resume_env/pyvenv.cfg](resume_env/pyvenv.cfg) — local venv config (ignored via .gitignore)
- __pycache__/ — cached bytecode (ignored)

## Environment
Create a `.env` file with:
```
OPENROUTER_API_KEY=your_api_key_here
```

The app uses `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))` in [app.py](app.py).

## Notes & troubleshooting
- If `pdflatex` is not installed, the app falls back to a plain PDF generator using ReportLab (`save_simple_pdf`).
- Ensure your LaTeX template placeholders match keys produced by `extract_resume_data` and the cleanup code in [`populate_latex_template`](app.py).
- Check logs printed by the server for AI errors and LaTeX compilation details.

## File map (quick links)
- [app.py](app.py)
- [requirements.txt](requirements.txt)
- [.env](.env)
- [.gitignore](.gitignore)
- [templates/main.tex](templates/main.tex)
- [front/index.html](front/index.html)
- [front/output/resume.tex](front/output/resume.tex)
- [resume_env/pyvenv.cfg](resume_env/pyvenv.cfg)

---

If you want, I can:
- add a ready-to-use `.env.example`,
- add a small curl example for the `/generate` endpoint,
- or create a minimal GitHub Actions workflow to check install + lint.
