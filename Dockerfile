FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY prompts ./prompts
COPY src ./src
COPY data/synthetic ./data/synthetic

RUN mkdir -p \
    /app/runtime/input \
    /app/runtime/output

ENTRYPOINT ["python", "src/ai/run_management_brief_pipeline_v0.1.py"]