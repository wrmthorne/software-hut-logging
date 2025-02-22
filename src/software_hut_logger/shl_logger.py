import os
from datetime import datetime
import logging
from pathlib import Path
import torch
from transformers import TrainerCallback
import json

from software_hut_logger.utils import upload_logs


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("SH_LOG_LEVEL", "WARNING"))


RUNS_BASE_DIR = Path.cwd() / Path("runs")


class SoftwareHutLogger(TrainerCallback):
    """Callback class for the huggingface trainer to log training and evaluation metrics in the required format
    for Software Hut teams.   
    """
    def __init__(self):
        self._initialized = False
        self._project_name = ""
        self._experiment_name = ""
        self._run_name = ""
        self._metric_file = ""
        self._run_metadata_file = ""

    def setup(self, args, state, model):
        self._initialized = True

        if not (_project_name := os.environ.get("SH_PROJECT_NAME")):
            raise ValueError("SH_PROJECT_NAME environment variable is not set")
        self._project_name = Path(_project_name)
        
        if not (_experiment_name := os.environ.get("SH_EXPERIMENT_NAME")):
            raise ValueError("SH_EXPERIMENT_NAME environment variable is not set")
        self._experiment_name = Path(_experiment_name)
        
        model_name = model.name_or_path if model else "unnamed-model"
        if not (_run_name := os.environ.get("SH_RUN_NAME")):
            _run_name = f"{model_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self._run_name = Path(_run_name)
        self._run_dir = RUNS_BASE_DIR / self._project_name / self._experiment_name / self._run_name
    
        if not self._run_dir.exists():
            self._run_dir.mkdir(parents=True)
            logger.debug(f"Created run directory: {self._run_dir}")

        self._metric_file = self._run_dir / "metrics.jsonl"
        if not self._metric_file.exists():
            self._metric_file.touch()

        logger.debug(f"SoftwareHutLogger initialized with project_name: {self._project_name}, "
                     f"experiment_name: {self._experiment_name}, "
                     f"run_name: {self._run_name}")
        
        self._run_metadata_file = self._run_dir / "run_metadata.json"
        with open(self._run_metadata_file, "w") as f:
            json.dump(args.to_dict() | {"training_state": "failed"}, f, indent=4)
        
    def on_train_begin(self, args, state, control, model=None, **kwargs):
        if not self._initialized:
            self.setup(args, state, model)

    def on_log(self, args, state, control, model=None, logs=None, **kwargs):
        if not self._initialized:
            self.setup(args, state, model)

        if state.is_world_process_zero:
            if state.is_world_process_zero:
                metrics = {}
                for k, v in logs.items():
                    if isinstance(v, (int, float)):
                        metrics[k] = v
                    elif isinstance(v, torch.Tensor) and v.numel() == 1:
                        metrics[k] = v.item()
                    elif isinstance(v, list):
                        metrics[k] = v
                    else:
                        logger.warning(f"Unsupported log value type: {type(v)} for key: {k}")

                if not "global_step" in metrics:
                    metrics["global_step"] = state.global_step

                with open(self._metric_file, "a") as f:
                    f.write(json.dumps({
                        **metrics,
                        "timestamp": datetime.now().isoformat(),
                    }) + "\n")

    def on_train_end(self, args, state, control, **kwargs):
        if self._initialized and state.is_world_process_zero:
            with open(self._run_metadata_file, "r+") as f:
                run_metadata = json.load(f)
                run_metadata["training_state"] = "successful"
                run_metadata["total_steps"] = state.global_step
                f.seek(0)
                json.dump(run_metadata, f, indent=4)
                f.truncate()

            upload_logs(self._run_dir)
    

