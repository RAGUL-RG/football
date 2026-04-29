from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ---------------------------
# LOAD DATA (simple direct access)
# ---------------------------
df = pd.read_csv("FIFA23_official_data.csv")

df.columns = df.columns.str.strip()
df = df.dropna(subset=["Name", "Overall", "Club"])

# ---------------------------
# HOME ROUTE
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

    top_players = (
        filtered.sort_values("Overall", ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    return render_template(
        "index.html",
        tables=top_players,
        clubs=clubs,
        selected_club=selected_club,
        min_rating=min_rating
    )

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run()
