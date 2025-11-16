FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY backend/ backend/
COPY frontend/ frontend/
COPY etl/core/ etl/core/
COPY .env.example .env

RUN pip install --no-cache-dir uv && \
    uv pip install --system duckdb fastapi pandas pyarrow pydantic pydantic-settings python-dotenv requests streamlit uvicorn

# Create startup script to run both backend and streamlit
RUN echo '#!/bin/bash\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
sleep 5\n\
streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0\n' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8501 8000

CMD ["/bin/bash", "/app/start.sh"]
