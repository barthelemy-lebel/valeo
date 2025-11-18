FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV VALEO_SECRET=CHANGE_ME
ENV SMTP_HOST=smtp.example.com
ENV SMTP_PORT=587
ENV FROM_EMAIL=noreply@valeo.example
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
