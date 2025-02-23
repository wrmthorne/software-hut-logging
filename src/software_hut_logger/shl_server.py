import argparse
import uvicorn
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import os
from pathlib import Path
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("SH_LOGGING_LEVEL", "WARNING"))

app = FastAPI()

CHUNK_SIZE = 1024 * 1024 * 10

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger.debug(f"Upload directory: {UPLOAD_DIR.absolute()}")

SH_API_KEY = os.environ.get("SH_API_KEY", "super-secret-api-key")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload-zip")
async def upload_zip(
    uploaded_run_file: UploadFile = File(...),
    project_name: str = Header(..., alias="X-Project-Name"),
    experiment_name: str = Header(..., alias="X-Experiment-Name"),
    api_key: str = Header(..., alias="X-API-Key")
) -> dict[str, str]:
    logger.debug(f"Received upload request for project {project_name}, experiment {experiment_name}, "
                 f"file {uploaded_run_file.filename} ({uploaded_run_file.content_type} - {uploaded_run_file.size} bytes)")
    if api_key != SH_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    try:
        if not uploaded_run_file.filename.endswith('.zip'):
            return JSONResponse(
                status_code=400,
                content={"message": "File must be a zip file"}
            )
        
        save_path = UPLOAD_DIR / Path(project_name) / Path(experiment_name) / Path(uploaded_run_file.filename).name
        logger.debug(f"Saving file to {save_path}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(save_path, "wb") as save_file:
            while buffer := await uploaded_run_file.read(CHUNK_SIZE):
                await save_file.write(buffer)
        
        return {
            "message": "File uploaded successfully",
            "project_name": project_name,
            "experiment_name": experiment_name,
            "saved_to": save_path
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )
    finally:
        uploaded_run_file.file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run server in background mode")
    parser.add_argument("--pid-file", default="uvicorn.pid", help="File to store the process ID")
    args = parser.parse_args()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        daemonize=args.daemon,
        pid_file=args.pid_file
    )