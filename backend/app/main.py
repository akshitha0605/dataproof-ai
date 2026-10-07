import os
import shutil
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.database import init_db, save_dataset_record, list_all_datasets
from app.utils.sample_generator import ensure_sample_datasets, SAMPLE_DIR
from app.agents.data_inspector import inspect_dataset
from app.routes import datasets, analysis, execution, verification

app = FastAPI(
    title="DATAPROOF AI",
    description="Every Answer. Every Number. Proven. Universal Proof-Carrying AI Data Analyst.",
    version="1.0.0"
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(datasets.router)
app.include_router(analysis.router)
app.include_router(execution.router)
app.include_router(verification.router)

@app.on_event("startup")
def startup_event():
    init_db()
    ensure_sample_datasets()
    
    # Auto-index sample datasets into DB if DB is empty
    existing = list_all_datasets()
    if not existing:
        upload_dir = Path(__file__).parent.parent / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        for sample_file in SAMPLE_DIR.glob("*"):
            if sample_file.is_file():
                dest_path = upload_dir / f"sample_{sample_file.name}"
                shutil.copy(sample_file, dest_path)
                try:
                    profile = inspect_dataset(str(dest_path))
                    profile["file_name"] = sample_file.name
                    save_dataset_record(
                        dataset_id=profile["id"],
                        file_name=sample_file.name,
                        file_path=str(dest_path),
                        file_type=sample_file.suffix.replace('.', '').upper(),
                        file_size_bytes=dest_path.stat().st_size,
                        profile_dict=profile
                    )
                except Exception as e:
                    print(f"Error profiling sample file {sample_file.name}: {e}")

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "DATAPROOF AI",
        "gemini_api_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    }

# Serve React static production frontend if built
dist_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return None
        target_file = dist_dir / full_path
        if target_file.exists() and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(dist_dir / "index.html")
