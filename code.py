from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# ---------------------------
# GLOBAL CACHE (Load once)
# ---------------------------
df = None

def load_data():
    global df
    if df is None:
        try:
            file_path = os.path.join(os.path.dirname(__file__), "fifa.csv")
            df = pd.read_csv(file_path)

            df.columns = df.columns.str.strip()

            # Validate required columns
            required_cols = ["Name", "Overall", "Club"]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing column: {col}")

            df.dropna(subset=required_cols, inplace=True)

        except Exception as e:
            print("❌ Data Load Error:", e)
            df = pd.DataFrame()

    return df

# ---------------------------
# HOME ROUTE
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    df = load_data()

    if df.empty:
        return "<h2>Error loading dataset. Check file or columns.</h2>"

    # Safe club list
    clubs = sorted(df["Club"].dropna().unique())

    # Get inputs
    selected_club = request.form.get("club", "All")
    min_rating = request.form.get("rating", 70)

    # Validate rating
    try:
        min_rating = int(min_rating)
    except:
        min_rating = 70

    # Filter
    filtered_df = df[df["Overall"] >= min_rating]

    if selected_club != "All":
        filtered_df = filtered_df[filtered_df["Club"] == selected_club]

    # Handle empty result
    if filtered_df.empty:
        top_players = []
    else:
        top_players = (
            filtered_df
            .sort_values(by="Overall", ascending=False)
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
# RUN (Render uses gunicorn)
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
