from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import os, json
import jwt
from datetime import datetime
import smtplib
from email.message import EmailMessage
from sqlmodel import SQLModel, Field, create_engine, Session, select

# config
VALEO_SECRET = os.environ.get("VALEO_SECRET", "CHANGE_ME")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@valeo.example")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./valeo.db")

app = FastAPI(title='Valéo Leads API')

engine = create_engine(DATABASE_URL, echo=False)

class LeadModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lead_id: str
    payload: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LeadIn(BaseModel):
    agency_email: EmailStr
    partial: bool = True

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, VALEO_SECRET, algorithms=['HS256'])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

def send_email(to_email: str, subject: str, html: str, text: str=''):
    msg = EmailMessage()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(text or 'Voir le HTML')
    msg.add_alternative(html, subtype='html')
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            if SMTP_USER and SMTP_PASS:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    except Exception as e:
        print('SMTP error', e)

@app.on_event('startup')
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post('/leads')
async def receive_lead(request: Request, authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    if not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Invalid auth scheme')
    token = authorization.split(' ', 1)[1]
    verify_jwt(token)
    body = await request.json()
    # store in sqlite
    with Session(engine) as session:
        lm = LeadModel(lead_id=body.get('lead_id', f"lead_{int(datetime.utcnow().timestamp())}"), payload=json.dumps(body))
        session.add(lm)
        session.commit()
    # if final submission, send email
    if not body.get('partial', True):
        agency = body.get('agency_email')
        if agency:
            subject = f"[Valéo] Nouvelle demande - {body.get('contact_name') or 'Sans nom'}"
            html = '<h2>Nouvelle demande d\'estimation</h2><ul>'
            for k, v in body.items():
                if k.startswith('_'): continue
                html += f'<li><strong>{k}</strong>: {v}</li>'
            html += '</ul>'
            send_email(agency, subject, html)
    return JSONResponse({'ok': True})
