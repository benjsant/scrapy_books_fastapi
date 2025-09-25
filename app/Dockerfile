FROM python:3.13.3

WORKDIR /app

# Installer les dépendances système si besoin
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code backend
COPY . .

# Exposer le port
EXPOSE 8000

# Lancer FastAPI avec Uvicorn en mode production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]