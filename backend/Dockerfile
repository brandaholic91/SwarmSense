# A kép verziója egyezzen a requirements.txt-ben rögzített playwright verzióval:
# a kép a hozzá tartozó Chromiumot és a rendszerkönyvtárait hozza.
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY --chown=pwuser:pwuser app ./app
COPY --chown=pwuser:pwuser schema.sql ./schema.sql
COPY --chown=pwuser:pwuser seed ./seed

USER pwuser

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
