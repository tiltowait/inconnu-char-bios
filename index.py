"""Present a basic webpage showing character info."""

import json
import os
from typing import Dict

from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client.inconnu
characters = db.characters

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Basic webpage with example."""
    with open("index.html", "r", encoding="utf-8") as html:
        return html.read()


@app.get("/offline", response_class=HTMLResponse)
async def offline_page():
    """Generate an offline test page."""
    with open("sample.json", "r", encoding="utf-8") as file:
        bio = json.load(file)
        return prepare_html(bio)


@app.get("/{charid}", response_class=HTMLResponse)
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
    biography = json.get("biography") or "Not set."
    description = json.get("description") or "Not set."
    image = json.get("image", "")

    with open("character.html", "r", encoding="utf-8") as html_file:
        html = html_file.read()
        return html.format(name=name, biography=biography, description=description, image=image)
