# CMA Agent — Mobile Deployment Guide

This project is prepared for deployment as a private Streamlit web app that can be opened from an iPhone.

## Recommended first deployment: Streamlit Community Cloud

1. Create a GitHub repository and upload this entire project folder.
2. Go to Streamlit Community Cloud and create a new app from the repository.
3. Select `app.py` as the main file.
4. Deploy.
5. Open the generated app URL on your iPhone.
6. In Safari, use **Share → Add to Home Screen**.

## API key — intentionally deferred

**An OpenAI API key is NOT required for the current learning-coach features.**

The current app uses deterministic Python logic for:

- adaptive question selection
- confidence tracking
- concept/explanation review
- targeted follow-up questions
- weak-domain and fragile-knowledge signals
- mastery tracking
- personalized study-plan logic

We will add an AI API only when it provides a meaningful learning benefit, such as deeper diagnosis, personalized explanations, generated examples, or conversational tutoring. This keeps the current version at **$0 in AI API usage**.

If/when the AI layer is added, the key should be stored as a deployment secret (for example, `OPENAI_API_KEY`) and never committed to GitHub.

## Important persistence note

The current CMA Agent uses SQLite for study history. Streamlit Community Cloud's local filesystem is not a durable database for production use. The app is therefore suitable for mobile testing, but **do not treat the first cloud deployment as the permanent home for your study history**.

The code supports a configurable database path through:

- `CMA_DB_PATH`

The next production step should move study history to a persistent hosted database. This is intentionally separated from the first deployment so we can test the learning experience before adding database infrastructure or cost.

## Local run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
