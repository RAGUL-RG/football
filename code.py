from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# ---------------------------
# LOAD + DATA CLEANING
# ---------------------------
df = pd.read_csv("FIFA23_official_data.csv")

# Standardize columns
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Remove duplicates
df = df.drop_duplicates()

# Handle missing values
df["Name"] = df["Name"].fillna("Unknown")
df["Club"] = df["Club"].fillna("No Club")

# Convert numeric safely
df["Overall"] = pd.to_numeric(df["Overall"], errors="coerce")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

df = df.dropna(subset=["Overall", "Age"])

# Outlier removal
df = df[df["Overall"].between(40, 99)]

# ---------------------------
# FEATURE ENGINEERING
# ---------------------------
df["Age_Group"] = pd.cut(
    df["Age"],
    bins=[0, 20, 25, 30, 40, 60],
    labels=["Teen", "Young", "Prime", "Veteran", "Old"]
)

df["Performance_Score"] = (
    df["Overall"] * 0.6 + df.get("Potential", df["Overall"]) * 0.4
)

# ---------------------------
# FLASK ROUTE
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    clubs = sorted(df["Club"].unique())

    selected_club = request.form.get("club", "All")
    min_rating = request.form.get("rating", 70)

    try:
        min_rating = int(min_rating)
    except:
        min_rating = 70

    filtered = df[df["Overall"] >= min_rating]

    if selected_club != "All":
        filtered = filtered[filtered["Club"] == selected_club]

    # ---------------------------
    # INSIGHTS
    # ---------------------------
    top_players = filtered.sort_values("Overall", ascending=False).head(10)

    avg_rating = round(filtered["Overall"].mean(), 2) if not filtered.empty else 0
    best_player = top_players.iloc[0]["Name"] if not top_players.empty else "N/A"

    club_stats = filtered.groupby("Club")["Overall"].mean().sort_values(ascending=False).head(5)

    # Convert for HTML
    players_data = top_players.to_dict(orient="records")
    club_data = club_stats.to_dict()

    # ---------------------------
    # RENDER
    # ---------------------------
    return render_template(
        "index.html",
        tables=players_data,
        clubs=clubs,
        selected_club=selected_club,
        min_rating=min_rating,
        avg_rating=avg_rating,
        best_player=best_player,
        club_data=club_data
    )

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run()
