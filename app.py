import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "players.json"

app = Flask(__name__)
CORS(app)


def load_players():
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def filter_players(players):
    search = request.args.get("search", "").strip().lower()
    club = request.args.get("club", "all")
    rating = request.args.get("rating", type=int)
    limit = request.args.get("limit", type=int)

    result = []
    for player in players:
        name = str(player.get("Name", "")).lower()
        player_club = str(player.get("Club", ""))
        overall = int(player.get("Overall") or 0)

        matches_search = not search or search in name
        matches_club = club == "all" or player_club == club
        matches_rating = rating is None or overall >= rating

        if matches_search and matches_club and matches_rating:
            result.append(player)

    if limit:
        result = result[:limit]

    return result


def build_stats(players):
    if not players:
        return {
            "totalPlayers": 0,
            "averageRating": 0,
            "topPlayer": None,
            "bestPotential": None,
            "clubs": [],
            "nationalities": [],
        }

    top_player = max(players, key=lambda player: int(player.get("Overall") or 0))
    best_potential = max(players, key=lambda player: int(player.get("Potential") or 0))
    average_rating = round(
        sum(int(player.get("Overall") or 0) for player in players) / len(players)
    )

    club_stats = {}
    nationality_stats = {}

    for player in players:
        club = player.get("Club") or "Unknown"
        nationality = player.get("Nationality") or "Unknown"
        overall = int(player.get("Overall") or 0)

        if club not in club_stats:
            club_stats[club] = {"club": club, "players": 0, "totalRating": 0}
        club_stats[club]["players"] += 1
        club_stats[club]["totalRating"] += overall

        nationality_stats[nationality] = nationality_stats.get(nationality, 0) + 1

    clubs = []
    for club in club_stats.values():
        clubs.append(
            {
                "club": club["club"],
                "players": club["players"],
                "averageRating": round(club["totalRating"] / club["players"]),
            }
        )

    clubs = sorted(clubs, key=lambda club: club["averageRating"], reverse=True)[:10]

    nationalities = [
        {"nationality": nationality, "players": count}
        for nationality, count in nationality_stats.items()
    ]
    nationalities = sorted(
        nationalities, key=lambda nationality: nationality["players"], reverse=True
    )[:10]

    return {
        "totalPlayers": len(players),
        "averageRating": average_rating,
        "topPlayer": top_player,
        "bestPotential": best_potential,
        "clubs": clubs,
        "nationalities": nationalities,
    }


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Football Player Statistics Analysis API",
            "routes": ["/health", "/api/players", "/api/stats"],
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/players")
@app.route("/players")
def players():
    return jsonify(filter_players(load_players()))


@app.route("/api/stats")
def stats():
    return jsonify(build_stats(load_players()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
