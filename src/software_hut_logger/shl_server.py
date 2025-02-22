import argparse
import uvicorn
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

SH_API_KEY = os.environ.get("SH_API_KEY", "super-secret-api-key")


@app.post("/upload-zip")
async def upload_zip(
    file: UploadFile = File(...),
    project_name: str = Header(..., alias="X-Project-Name"),
    experiment_name: str = Header(..., alias="X-Experiment-Name"),
    api_key: str = Header(..., alias="X-API-Key")
) -> dict[str, str]:
    if api_key != SH_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    try:
        if not file.filename.endswith('.zip'):
            return JSONResponse(
                status_code=400,
                content={"message": "File must be a zip file"}
            )
        
        file_path = UPLOAD_DIR / project_name / experiment_name / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "project_name": project_name,
            "experiment_name": experiment_name
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )


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