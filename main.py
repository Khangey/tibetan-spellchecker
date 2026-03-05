"""
Tibetan Spellchecker Web Service
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from spellcheck import load_dictionary, spellcheck_text

app = FastAPI(
    title="Tibetan Spellchecker",
    description="藏文拼写检查网页服务 - 基于 tibetan-spellchecker 词典资源",
)

BASE_DIR = Path(__file__).resolve().parent
VALID_SYLLABLES = load_dictionary(BASE_DIR)


class SpellcheckRequest(BaseModel):
    text: str


class SpellcheckResponse(BaseModel):
    results: list
    text: str
    error_count: int


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the frontend."""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/spellcheck", response_model=SpellcheckResponse)
async def spellcheck(req: SpellcheckRequest):
    """Check Tibetan text for spelling errors."""
    results = spellcheck_text(req.text, VALID_SYLLABLES)
    error_count = sum(1 for r in results if not r["valid"])
    return SpellcheckResponse(
        results=results,
        text=req.text,
        error_count=error_count,
    )


@app.get("/api/check/{syllable}")
async def check_syllable(syllable: str):
    """Check a single syllable."""
    return {
        "syllable": syllable,
        "valid": syllable in VALID_SYLLABLES,
    }


@app.get("/api/stats")
async def stats():
    """Get dictionary statistics."""
    return {
        "valid_syllables_count": len(VALID_SYLLABLES),
    }


# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    fonts_dir = static_dir / "fonts"
    if fonts_dir.exists():
        app.mount("/fonts", StaticFiles(directory=str(fonts_dir)), name="fonts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
