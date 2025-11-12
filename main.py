import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Appointment, QuoteRequest, Service, GalleryImage

app = FastAPI(title="Swarajyache Armar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Swarajyache Armar Backend Running"}


@app.get("/api/services")
def list_services():
    """List available services. If DB empty, return sensible defaults."""
    try:
        items = get_documents("service")
        # convert ObjectId to str and floats
        def normalize(doc):
            doc = {**doc}
            if doc.get("_id"):
                doc["id"] = str(doc.pop("_id"))
            return doc
        normalized = [normalize(d) for d in items]
        if normalized:
            return normalized
    except Exception:
        # If database not configured, fall back to static
        pass

    # Fallback defaults
    return [
        {
            "title": "Modular Kitchen",
            "description": "Custom modular kitchens with premium finishes and hardware.",
            "starting_price": 1499.0,
            "unit": "per running ft",
            "featured": True,
        },
        {
            "title": "Wardrobes",
            "description": "Sliding and hinged door wardrobes tailored to your space.",
            "starting_price": 999.0,
            "unit": "per sq ft",
            "featured": True,
        },
        {
            "title": "TV Units",
            "description": "Modern media units with storage and lighting.",
            "starting_price": 799.0,
            "unit": "per unit",
            "featured": False,
        },
    ]


@app.get("/api/gallery")
def list_gallery():
    """Return gallery images from DB or static if none."""
    try:
        items = get_documents("galleryimage", limit=30)
        def normalize(doc):
            doc = {**doc}
            if doc.get("_id"):
                doc["id"] = str(doc.pop("_id"))
            return doc
        normalized = [normalize(d) for d in items]
        if normalized:
            return normalized
    except Exception:
        pass

    return [
        {"url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85", "title": "Modular Kitchen"},
        {"url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0", "title": "Wardrobe"},
        {"url": "https://images.unsplash.com/photo-1493666438817-866a91353ca9", "title": "TV Unit"},
        {"url": "https://images.unsplash.com/photo-1598300187395-21b5b3a5b1d4", "title": "Storage"},
        {"url": "https://images.unsplash.com/photo-1617093727343-374698b9362d", "title": "Kitchen Island"},
    ]


class AppointmentCreate(Appointment):
    pass


@app.post("/api/appointments")
def create_appointment(payload: AppointmentCreate):
    """Book an appointment. Stores in DB with timestamps."""
    try:
        inserted_id = create_document("appointment", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        # If DB not available, still acknowledge but mark as not persisted
        return {"status": "received", "message": "Database not available in this environment", "error": str(e)[:120]}


class QuoteRequestCreate(QuoteRequest):
    pass


@app.post("/api/quotes")
def create_quote_request(payload: QuoteRequestCreate):
    try:
        inserted_id = create_document("quoterequest", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        return {"status": "received", "message": "Database not available in this environment", "error": str(e)[:120]}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
