# Football Player Statistics Python Backend

This is the Python Flask backend for the Football Player Statistics Analysis mini project.

The backend can read either:

```text
FIFA23_official_data.xlsx
```

or:

```text
data/players.json
```

## Run Locally

```bash
cd backend-python
pip install -r requirements.txt
python app.py
```

The server runs at:

```text
http://localhost:5000
```

## API Routes

```text
GET /health
GET /api/players
GET /api/players?search=messi
GET /api/players?club=Inter%20Miami
GET /api/players?rating=85
GET /api/players?limit=20
GET /api/stats
```

## Render Hosting

Root Directory:

```text
backend-python
```

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn app:app
```
