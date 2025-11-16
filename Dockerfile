FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY backend/ backend/
COPY frontend/ frontend/
COPY etl/core/ etl/core/
COPY .env.example .env

RUN pip install --no-cache-dir uv && \
    uv pip install --system duckdb fastapi pandas pyarrow pydantic pydantic-settings python-dotenv requests streamlit uvicorn plotly

# Start backend in background, then run streamlit in foreground
RUN echo '#!/bin/bash\n\
echo "Starting backend server..."\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
echo "Waiting for backend to be ready..."\n\
sleep 5\n\
echo "Starting Streamlit dashboard on port ${PORT:-8501}..."\n\
streamlit run frontend/streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true\n' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8501 8000

CMD ["/bin/bash", "/app/start.sh"]
