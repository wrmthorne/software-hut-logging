from dataclasses import dataclass
import json
import logging
import os
import shutil
from pathlib import Path

import requests


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("SH_LOG_LEVEL", "WARNING"))


@dataclass
class ScriptArguments:
    model_name_or_path: str = "t5-small"
    max_length: int = 512
    num_train_samples: int = 25_000
    num_test_samples: int = 1000
    project_name: str = "test-project"
    experiment_name: str = "test-experiment"


def upload_logs(file_path: Path):
    zipped_path = Path("/tmp") / file_path.name
    shutil.make_archive(zipped_path, 'zip', file_path)

    headers = {'X-API-Key': os.environ.get("SH_API_KEY")}
    with open(zipped_path, 'rb') as f:
        files = {'file': (zipped_path.with_suffix(".zip"), f, 'application/zip')}
        upload_url = os.environ.get("SH_UPLOAD_URL", "0.0.0.0")
        upload_port = os.environ.get("SH_UPLOAD_PORT", 8000)
        response = requests.post(f"http://{upload_url}:{upload_port}/upload-zip", files=files, headers=headers)
        logger.debug(json.dumps(response.json(), indent=4))