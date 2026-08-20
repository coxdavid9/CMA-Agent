# CMA Agent — Mobile Deployment Guide

This project is prepared for deployment as a private Streamlit web app that can be opened from an iPhone.

## Recommended first deployment: Streamlit Community Cloud

1. Create a GitHub repository and upload this entire project folder.
2. Go to Streamlit Community Cloud and create a new app from the repository.
3. Select `app.py` as the main file.
4. In the app settings, open **Secrets** and add:

```toml
OPENAI_API_KEY = "your-key"
```

5. Deploy.
6. Open the generated app URL on your iPhone.
7. In Safari, use **Share → Add to Home Screen**.

Do not put the API key in the repository or inside `.env` when deploying to GitHub. Use Streamlit Secrets.

## Important persistence note

The current CMA Agent uses SQLite for study history and the OpenAI Agents SDK SQLite session for agent memory. Streamlit Community Cloud's local filesystem is not a durable database for production use. The app is therefore deployment-ready for mobile testing, but **do not treat the first cloud deployment as the permanent home for your study history**.

The code now supports configurable database paths through:

- `CMA_DB_PATH`
- `CMA_AGENT_MEMORY_DB`

The next production step should move these two stores to a persistent hosted database. This is intentionally separated from the first deployment so we can test the mobile experience before adding database infrastructure or cost.

## Local run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## API key

The app expects `OPENAI_API_KEY`. For local use, create `.env` in the project root. For Streamlit Cloud, use the Secrets panel instead.
