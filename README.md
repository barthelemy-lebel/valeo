# Valéo API (api/)
FastAPI app to receive signed leads from the Valéo widget, store them in SQLite and send emails on final submission.

## Quickstart (local)
1. create virtualenv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. set env vars
export VALEO_SECRET="YOUR_SHARED_SECRET"
export SMTP_HOST="smtp.mailprovider"
export SMTP_PORT=587
export SMTP_USER="smtp_user"
export SMTP_PASS="smtp_pass"
export FROM_EMAIL="noreply@valeo.example"
export DATABASE_URL="sqlite:///./valeo.db"

3. run
uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Deploy to Render
- Create a new Web Service on Render
- Connect this repo (or upload)
- Set Build Command: docker build -t valeo .
- Set Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
- Add environment variables (VALEO_SECRET, SMTP_*, FROM_EMAIL)
- After deploy, use the service URL as data-valeo-endpoint in the widget snippet

## Notes
- SQLite is used by default (file valeo.db)
- For production, swap to managed Postgres and update DATABASE_URL
