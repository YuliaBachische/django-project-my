FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN pip install --upgrade pip "poetry==1.8.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY api .

CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:7900"]



