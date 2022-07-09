"""Present a basic webpage showing character info."""

import json
import os
from typing import Dict

from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client.inconnu
characters = db.characters

app = FastAPI()
app.mount("/favicon", StaticFiles(directory="favicon"), name="favicon")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Basic webpage with example."""
    with open("index.html", "r", encoding="utf-8") as html:
        return html.read()


@app.get("/test", response_class=HTMLResponse)
async def offline_page():
    """Generate an offline test page."""
    with open("sample.json", "r", encoding="utf-8") as file:
        bio = json.load(file)
        return prepare_html(bio)


@app.get("/profile/{charid}", response_class=HTMLResponse)
async def display_character_bio(charid: str):
    """Display character biography detail."""
    if not ObjectId.is_valid(charid):
        raise HTTPException(400, detail="Improper character ID.")

    oid = ObjectId(charid)
    bio = await characters.find_one(
        {"_id": oid}, {"name": 1, "biography": 1, "description": 1, "image": 1}
    )
    if bio is None:
        raise HTTPException(404, detail="Character not found.")

    # Got the character; return the HTML
    return prepare_html(bio)


def prepare_html(json: Dict[str, str]) -> str:
    """Prep the character HTML page."""
    name = json["name"]
    biography = json.get("biography") or gen_not_set()
    description = json.get("description") or gen_not_set()
    image = gen_img(json.get("image"), name)

    with open("profile.html", "r", encoding="utf-8") as html_file:
        html = html_file.read()
        return html.format(name=name, biography=biography, description=description, image=image)


def gen_not_set() -> str:
    """Generate a styled "Not set" text."""
    return '<em class="text-muted">Not set.</em>'


def gen_img(image: str, name: str) -> str:
    """Generate the img tag or specify unset."""
    if image:
        return f'<img src="{image}" alt="{name}" class="rounded img-fluid">'
    return '<p class="text-muted text-center"><em>No image set.</em></p>'
