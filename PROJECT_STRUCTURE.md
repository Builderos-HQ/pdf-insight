# Project Structure

```text
pdf-insight/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
└── screenshots/
    ├── home.jpg
    ├── analysis.jpg
    └── application.jpg

## Application Flow

Freelance Job PDF
        ↓
     PyMuPDF
        ↓
   Extract Text
        ↓
    OpenAI API
        ↓
 Structured Analysis
        ↓
 ┌──────┼────────┐
 ↓      ↓        ↓
Fit   Risks   Skill Match
 ↓      ↓        ↓
     Recommendation
           ↓
 Application Message