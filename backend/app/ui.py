"""Serve the HuLex website from the existing FastAPI process.

Call mount_site(app) after existing app.include_router(...) calls in app/main.py.
This intentionally leaves the existing '/' API route and /docs untouched.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FRONTEND = Path(__file__).resolve().parents[2] / 'frontend'


def mount_site(app: FastAPI) -> None:
    html = FRONTEND / 'index.html'
    assets = FRONTEND / 'assets'
    if not html.is_file() or not assets.is_dir():
        raise RuntimeError(
            'HuLex frontend files not found. Copy the upgrade frontend/ folder '
            'to the repository root, beside backend/.'
        )

    app.mount('/site-assets', StaticFiles(directory=str(assets)), name='hulex_site_assets')

    @app.get('/app', include_in_schema=False)
    def hulex_frontend() -> FileResponse:
        return FileResponse(str(html), media_type='text/html')
