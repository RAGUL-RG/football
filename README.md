# Football Player Statistics Backend

This is the backend API for the Football Player Statistics Analysis mini project.

## Run Locally

```bash
cd backend
npm start
```

The server runs at:

```text
http://localhost:3000
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

## JSON Format

The frontend expects player records like:

```json
[
  {
    "ID": 158023,
    "Name": "Messi",
    "Age": 35,
    "Nationality": "Argentina",
    "Overall": 91,
    "Potential": 91,
    "Club": "Paris Saint-Germain",
    "Preferred Foot": "Left"
  }
]
```

## Deployment

You can deploy this backend on Render as a Web Service.

Build command:

```text
npm install
```

Start command:

```text
npm start
```
