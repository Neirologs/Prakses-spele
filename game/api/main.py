import secrets
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from api.db import get_connection, hash_password

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="War Breakout API")


@app.get("/static/style.css", include_in_schema=False)
def stylesheet():
    for folder in (STATIC_DIR, BASE_DIR / "templates"):
        if (folder / "style.css").exists():
            return FileResponse(folder / "style.css", media_type="text/css")
    raise HTTPException(404, "style.css not found")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# The game sends time in centiseconds (whole number). here it gets converted to 01:23.45
def format_time(centiseconds):
    minutes, rest = divmod(int(centiseconds), 6000)
    return f"{minutes:02d}:{rest // 100:02d}.{rest % 100:02d}"


templates.env.filters["laiks"] = format_time


# ---------- Models (what data to send) ----------

class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=25)
    password: str = Field(min_length=3, max_length=100)


class ScoreIn(BaseModel):
    score: int = Field(gt=0) # the name is found by the token


# ---------- Helper  function ----------

def get_top(limit):
    # Spēlē mazāks laiks ir labāks, tāpēc ASC (nevis DESC)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT player, score FROM scores "
            "ORDER BY score ASC, id ASC LIMIT ?", (limit,)).fetchall()
    return [{"player": p, "score": s} for p, s in rows]


# ---------- API adreses ----------

@app.get("/hello")
def hello():
    return {"message": "Sveiki!"}


@app.post("/register", status_code=201)
def register(user: UserIn):
    name = user.name.strip()
    if len(name) < 2:
        raise HTTPException(400, "Vārdam jābūt vismaz 2 simboliem")
    try:
        with get_connection() as conn:
            exists = conn.execute(
                "SELECT 1 FROM players WHERE name = ?", (name,)).fetchone()
            if exists:
                raise HTTPException(400, "Vārds jau aizņemts")
            conn.execute(
                "INSERT INTO players (name, password_hash) VALUES (?, ?)",
                (name, hash_password(user.password)))
    except sqlite3.IntegrityError:    # two registrations at the same time with the same name
        raise HTTPException(400, "Vārds jau aizņemts")
    return {"name": name}


@app.post("/login")
def login(user: UserIn):
    name = user.name.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM players WHERE name = ?",
            (name,)).fetchone()
        if row is None or row[0] != hash_password(user.password):
            raise HTTPException(401, "Nepareizs vārds vai parole")
        token = secrets.token_hex(16)
        conn.execute(
            "UPDATE players SET token = ? WHERE name = ?", (token, name))
    return {"token": token, "name": name}


@app.post("/scores", status_code=201)
def add_score(item: ScoreIn, token: Optional[str] = Header(default=None)):
    if not token:
        raise HTTPException(401, "Nav pieteicies")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT name FROM players WHERE token = ?", (token,)).fetchone()
        if row is None:
            raise HTTPException(401, "Nav pieteicies")
        conn.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (row[0], item.score))
    return {"player": row[0], "score": item.score}


@app.get("/scores/top")
def top():
    return get_top(10)


@app.get("/players/{name}/stats")
def player_stats(name: str):
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM players WHERE name = ?", (name,)).fetchone()
        if exists is None:
            raise HTTPException(404, "Šāda spēlētāja nav")
        games, best = conn.execute(
            "SELECT COUNT(*), MIN(score) FROM scores WHERE player = ?",
            (name,)).fetchone()
    return {"player": name, "games": games, "best": best}


# ---------- Homepage (Jinja) ----------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def leaderboard_page(request: Request):
    return templates.TemplateResponse(
        request, "leaderboard.html", {"scores": get_top(5)})


@app.get("/rules", response_class=HTMLResponse, include_in_schema=False)
def rules_page(request: Request):
    return templates.TemplateResponse(request, "rules.html", {})