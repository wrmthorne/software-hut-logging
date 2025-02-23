from dataclasses import dataclass
import json
import logging
import os
import shutil
from pathlib import Path

import requests


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("SH_LOGGING_LEVEL", "WARNING"))


@dataclass
class ScriptArguments:
    model_name_or_path: str = "t5-small"
    max_length: int = 512
    num_train_samples: int = 25_000
    num_test_samples: int = 1000
    project_name: str = "test-project"
    experiment_name: str = "test-experiment"
    run_dir: str = "runs"


@dataclass
class ServerArguments:
    api_key: str
    project_name: str
    experiment_name: str
    run_name: str

    def to_dict(self):
        return {
            "X-API-Key": self.api_key,
            "X-Project-Name": self.project_name,
            "X-Experiment-Name": self.experiment_name,
            "X-Run-Name": self.run_name
        }


def upload_run(file_path: Path):
    upload_url = os.environ.get("SH_UPLOAD_URL", "0.0.0.0")
    upload_port = os.environ.get("SH_UPLOAD_PORT", 8000)

    headers = ServerArguments(
        api_key=os.environ.get("SH_API_KEY"),
        project_name=os.environ.get("SH_PROJECT_NAME"),
        experiment_name=os.environ.get("SH_EXPERIMENT_NAME"),
        run_name=os.environ.get("SH_RUN_NAME")
    )

    if requests.get(f"http://{upload_url}:{upload_port}/health").status_code != 200:
        logger.warning(f"Server at {upload_url}:{upload_port} is not running")
        return
    
    zipped_path = Path("/tmp") / file_path.name
    zipped_file = zipped_path.with_suffix(".zip")
    shutil.make_archive(zipped_path, 'zip', file_path)

    logger.debug(f"Uploading run {file_path} to {upload_url}:{upload_port}")
    
    with open(zipped_file, 'rb') as f:
        files = {'uploaded_run_file': (str(zipped_file), f, 'application/zip')}
        response = requests.post(f"http://{upload_url}:{upload_port}/upload-zip", files=files, headers=headers.to_dict())
        logger.debug(f"{json.dumps(response.json())}")