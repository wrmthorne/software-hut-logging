import argparse
from datetime import datetime
from pathlib import Path
import sys
import os
import signal
import subprocess
import time
from typing import Optional
import psutil


def create_parser():
    parser = argparse.ArgumentParser(description='Software Hut Logger CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # dataset command
    dataset_parser = subparsers.add_parser('build-example-dataset', help='Build example dataset')
    dataset_parser.add_argument('--save_dir', '--save_dir', type=str, default='example_dataset',
                                help='Path to save the example dataset')
    dataset_parser.add_argument('--num_samples', '--num_samples', type=int, default=-1,
                                help='Number of samples to save')

    # upload-run command
    upload_run_parser = subparsers.add_parser('upload-run', help='Upload run to the server')
    upload_run_parser.add_argument('--run-dir', '--run_dir', dest='run_dir', type=str, default='example_run',
                                 help='Path to run directory')
    upload_run_parser.add_argument('--api-key', '--api_key', dest='api_key', type=str, default='super-secret-api-key',
                                 help='API key for authentication')
    upload_run_parser.add_argument('--upload-url', '--upload_url', type=str, default='0.0.0.0',
                                 help='URL or IP address of receiving server')
    upload_run_parser.add_argument('--upload-port', '--upload_port', type=int, default=8000,
                                 help='Port number of receiving server')

    # Server command
    server_parser = subparsers.add_parser('server', help='Run server operations')
    server_subparsers = server_parser.add_subparsers(dest='server_command', required=True)
    
    server_parser.add_argument('--pid-file', '--pid_file', dest='pid_file', type=str, default='/tmp/uvicorn.pid',
                               help='File containing the process ID')
    
    # Start server command
    start_parser = server_subparsers.add_parser('start', help='Start the demo-server')
    start_parser.add_argument('-q', '--quiet', action='store_true',
                            help='Launch server in background and exit')
    start_parser.add_argument('--api-key', '--api_key', dest='api_key', type=str, default='super-secret-api-key',
                            help='API key for authentication')
    start_parser.add_argument('--upload-url', '--upload_url', type=str, default='0.0.0.0',
                            help='URL or IP address of receiving server')
    start_parser.add_argument('--upload-port', '--upload_port', type=int, default=8000,
                            help='Port number of receiving server')
    start_parser.add_argument('--workers', type=int, default=1,
                            help='Number of worker processes')

    # Stop server command
    stop_parser = server_subparsers.add_parser('stop', help='Stop the demo-server')

    # Train command
    train_parser = subparsers.add_parser('train', help='Run training operations')
    
    parser.add_argument('--project-name', '--project_name', type=str, default='test-project',
                        help='Name of the project')
    parser.add_argument('--experiment-name', '--experiment_name', type=str, default='test-experiment',
                        help='Name of the experiment')
    parser.add_argument('--run-name', '--run_name', type=str, default=None,
                        help='Name of the run. If not provided, the current timestamp will be used')
    
    return parser


def handle_train_command(train_args):
    accelerate_config_path = Path(__file__).parent / "accelerate_config.yml"
    train_script_path = Path(__file__).parent / "shl_train.py"
    cmd = [
        "accelerate",
        "launch",
        "--config_file",
        str(accelerate_config_path),
        str(train_script_path),
    ]
    
    cmd.extend(train_args)
    
    try:
        subprocess.run(cmd)
    except ImportError as e:
        print(f"software-hut-logger must be installed with train dependency group to use the train command")
        print(f"pip install software-hut-logger[train]")
        sys.exit(1)


def handle_build_example_dataset_command(args):
    dataset_script_path = Path(__file__).parent / "shl_dataset.py"
    cmd = [
        "python3",
        str(dataset_script_path),
    ]
    subprocess.run(cmd)


def read_pid_file(pid_file: str) -> Optional[int]:
    try:
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_pid_file(pid_file: str, pid: int):
    with open(pid_file, 'w') as f:
        f.write(str(pid))


def remove_pid_file(pid_file: str):
    try:
        os.remove(pid_file)
    except FileNotFoundError:
        pass


def is_process_running(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False


def handle_test_log_command(args):
    print(f"Running upload-run with settings:")
    print(f"Run directory: {args.run_dir}")
    print(f"API key: {'*' * len(args.api_key) if args.api_key else 'None'}")
    print(f"Upload URL: {args.upload_url}")
    print(f"Upload port: {args.upload_port}")

    os.environ["SH_API_KEY"] = args.api_key
    os.environ["SH_UPLOAD_URL"] = args.upload_url
    os.environ["SH_UPLOAD_PORT"] = str(args.upload_port)
    
    from . import upload_run
    upload_run(args.run_dir, args.api_key, args.upload_url, args.upload_port)


def start_server(args):
    existing_pid = read_pid_file(args.pid_file)
    if existing_pid and is_process_running(existing_pid):
        print(f"Server is already running with PID {existing_pid}")
        sys.exit(1)

    os.environ["SH_API_KEY"] = args.api_key
    os.environ["SH_UPLOAD_URL"] = args.upload_url
    os.environ["SH_UPLOAD_PORT"] = str(args.upload_port)

    cmd = [
        "uvicorn",
        "software_hut_logger.shl_server:app",
        "--host", str(args.upload_url),
        "--port", str(args.upload_port),
        "--workers", str(args.workers)
    ]

    if args.quiet:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        write_pid_file(args.pid_file, process.pid)
        print(f"Server started in background with PID {process.pid}")
        sys.exit(0)
    else:
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nServer stopped")

def stop_server(args):
    pid = read_pid_file(args.pid_file)
    if not pid:
        print("No running server found (PID file not found)")
        return

    if not is_process_running(pid):
        print(f"No running server found with PID {pid}")
        remove_pid_file(args.pid_file)
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent shutdown signal to server (PID {pid})")
        
        for _ in range(10):
            if not is_process_running(pid):
                break
            time.sleep(0.5)
        
        # Force kill if still running
        if is_process_running(pid):
            os.kill(pid, signal.SIGKILL)
            print(f"Force killed server process (PID {pid})")
    except ProcessLookupError:
        print(f"Process {pid} not found")
    finally:
        remove_pid_file(args.pid_file)


def main():
    parser = create_parser()

    # Special handling to forward train --help to shl train --help
    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        if ('--help' in sys.argv or '-h' in sys.argv):
            train_script_path = Path(__file__).parent / "shl_train.py"
            subprocess.run(["python3", str(train_script_path), "--help"])
            sys.exit(0)
        
    args, train_args = parser.parse_known_args()

    os.environ["SH_PROJECT_NAME"] = args.project_name
    os.environ["SH_EXPERIMENT_NAME"] = args.experiment_name
    if "--run-name" in train_args:
        os.environ["SH_RUN_NAME"] = train_args[train_args.index("--run-name") + 1]
    elif "--run_name" in train_args:
        os.environ["SH_RUN_NAME"] = train_args[train_args.index("--run_name") + 1]
    else:
        os.environ["SH_RUN_NAME"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if args.command == 'train':
        handle_train_command(train_args)
    elif args.command == 'build-example-dataset':
        handle_build_example_dataset_command(args)
    elif args.command == 'upload-run':
        handle_test_log_command(args)
    elif args.command == 'server':
        if args.server_command == 'start':
            start_server(args)
        elif args.server_command == 'stop':
            stop_server(args)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()