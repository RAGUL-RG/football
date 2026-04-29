const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const DATA_PATH = path.join(__dirname, "data", "players.json");

function readPlayers() {
  const raw = fs.readFileSync(DATA_PATH, "utf8");
  return JSON.parse(raw);
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept"
  });
  res.end(JSON.stringify(payload));
}

function notFound(res) {
  sendJson(res, 404, {
    error: "Route not found",
    routes: ["/", "/health", "/api/players", "/api/stats"]
  });
}

function filterPlayers(players, url) {
  const search = (url.searchParams.get("search") || "").toLowerCase();
  const club = url.searchParams.get("club") || "all";
  const rating = Number(url.searchParams.get("rating") || 0);
  const limit = Number(url.searchParams.get("limit") || 0);

  let result = players.filter((player) => {
    const matchesSearch = !search || player.Name.toLowerCase().includes(search);
    const matchesClub = club === "all" || player.Club === club;
    const matchesRating = !rating || Number(player.Overall) >= rating;
    return matchesSearch && matchesClub && matchesRating;
  });

  if (limit > 0) {
    result = result.slice(0, limit);
  }

  return result;
}

function getStats(players) {
  if (!players.length) {
    return {
      totalPlayers: 0,
      averageRating: 0,
      topPlayer: null,
      bestPotential: null,
      clubs: [],
      nationalities: []
    };
  }

  const topPlayer = players.reduce((best, player) =>
    Number(player.Overall) > Number(best.Overall) ? player : best
  );

  const bestPotential = players.reduce((best, player) =>
    Number(player.Potential) > Number(best.Potential) ? player : best
  );

  const averageRating = Math.round(
    players.reduce((sum, player) => sum + Number(player.Overall || 0), 0) / players.length
  );

  const clubMap = new Map();
  const nationMap = new Map();

  players.forEach((player) => {
    const club = player.Club || "Unknown";
    const nationality = player.Nationality || "Unknown";

    if (!clubMap.has(club)) {
      clubMap.set(club, { club, totalRating: 0, players: 0 });
    }
    const clubData = clubMap.get(club);
    clubData.totalRating += Number(player.Overall || 0);
    clubData.players += 1;

    nationMap.set(nationality, (nationMap.get(nationality) || 0) + 1);
  });

  const clubs = Array.from(clubMap.values())
    .map((club) => ({
      club: club.club,
      players: club.players,
      averageRating: Math.round(club.totalRating / club.players)
    }))
    .sort((a, b) => b.averageRating - a.averageRating)
    .slice(0, 10);

  const nationalities = Array.from(nationMap.entries())
    .map(([nationality, players]) => ({ nationality, players }))
    .sort((a, b) => b.players - a.players)
    .slice(0, 10);

  return {
    totalPlayers: players.length,
    averageRating,
    topPlayer,
    bestPotential,
    clubs,
    nationalities
  };
}

const server = http.createServer((req, res) => {
  if (req.method === "OPTIONS") {
    sendJson(res, 200, { ok: true });
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);

  try {
    if (url.pathname === "/") {
      sendJson(res, 200, {
        message: "Football Player Statistics Analysis API",
        routes: ["/health", "/api/players", "/api/stats"]
      });
      return;
    }

    if (url.pathname === "/health") {
      sendJson(res, 200, { status: "ok" });
      return;
    }

    if (url.pathname === "/api/players" || url.pathname === "/players") {
      const players = readPlayers();
      sendJson(res, 200, filterPlayers(players, url));
      return;
    }

    if (url.pathname === "/api/stats") {
      const players = readPlayers();
      sendJson(res, 200, getStats(players));
      return;
    }

    notFound(res);
  } catch (error) {
    sendJson(res, 500, {
      error: "Server error",
      message: error.message
    });
  }
});

server.listen(PORT, () => {
  console.log(`Football Player Statistics API running at http://localhost:${PORT}`);
});
