from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.auth import router as auth_router
from app.complaints import router as complaints_router
from app.admin import router as admin_router
from app.services.scheduler import shutdown_scheduler, start_scheduler
from app.notifications import router as notifications_router
from app.services.uploads import UPLOADS_DIR

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()

app = FastAPI(title="CivicConnect API", version="0.1.0", lifespan=lifespan)
allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
allowed_origins.extend(
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(allowed_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(admin_router)
app.include_router(notifications_router)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CivicConnect API</title>
    <style>
      :root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #f3f7f8; }
      body { min-height: 100vh; margin: 0; display: grid; place-items: center; }
      main { width: min(560px, calc(100% - 40px)); padding: 36px; border: 1px solid #dce7e8; border-radius: 18px; background: white; box-shadow: 0 14px 40px #163b4b12; }
      h1 { margin: 0 0 10px; font-size: 30px; }
      p { color: #526873; line-height: 1.6; }
      nav { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 26px; }
      a { padding: 11px 16px; border-radius: 10px; color: white; background: #087e83; font-weight: 650; text-decoration: none; }
      a.secondary { color: #17646a; background: #e4f3f2; }
      code { color: #31515e; }
    </style>
  </head>
  <body>
    <main>
      <h1>CivicConnect API</h1>
      <p>The backend is running. Explore the interactive API documentation or check the service health.</p>
      <nav aria-label="API links">
        <a href="/docs">Open API docs</a>
        <a class="secondary" href="/health">Health status</a>
      </nav>
      <p>Authentication routes: <code>POST /auth/register</code> and <code>POST /auth/login</code>.</p>
    </main>
  </body>
</html>"""


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
