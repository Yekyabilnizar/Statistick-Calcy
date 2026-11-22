FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements-web.txt .
RUN pip install -r requirements-web.txt

# Mesin perhitungan (tanpa Streamlit) + website
COPY design_engine.py posthoc_ext.py reg_core.py reg_models1.py reg_models2.py reg_models3.py reg_samples.py stats_engine.py flows.py flows_en.py ./
COPY web ./web

EXPOSE 10000
CMD ["sh", "-c", "uvicorn web.main:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]
