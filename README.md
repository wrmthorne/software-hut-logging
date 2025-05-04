# Software Hut Logger

A package containing the logger demo for Software Hut using Hugging Face 🤗 Transformers Trainer. 

**Important Notes:**
- If you find anything is broken or confusing, please open an issue so that all teams can benefit from any explanations and fixes.
- This module was developed on linux and is untested on Windows. I would recommend using WSL2 if you don't have a linux machine available but Windows might work. I won't be able to support Windows specific issues.
- You won't need to run the training script but if you **really** want to, linux/WSL2 and CUDA>=12.1 on an NVIDIA GPU are required.

## Index
- **[Installation & Setup](#2-installation--setup)**: Instructions for setting up the environment.
- **[Usage](#3-usage)**: How to use the software after installation.
- **[Commands](#31-commands)**: List of available commands and their descriptions.
- **[Metadata File Contents](#4-metadata-file-contents)**: Details about the contents of the metadata file.

## TODO
- [ ] Finish documentation
- [ ] Add system monitoring

## 1. Installation & Setup

```bash
# Create a virtual environment
python3 -m venv shl-demo-venv
source shl-demo-venv/bin/activate
pip install software-hut-logger
```

`NOTE:` If you want to edit the code or rerun the training script for any reason, let me know and I'll add instructions.


## 2. Usage

If installed correctly, the package should be available as a command-line tool. 

```bash
# Both commands are equivalent
shl <command> [ --project-name <project-name> ] [ --experiment-name <experiment-name> ] [ --run-name <run-name> ] [...command-specific-options]

software-hut-logger <command> [ --project-name <project-name> ] [ --experiment-name <experiment-name> ] [ --run-name <run-name> ] [...command-specific-options]
```

`NOTE:` Anywhere that "-" is used in an argument name, "_" is also valid.

<details>
<summary><b>EXPAND:</b> What the hell is this command description syntax?</summary>

#### Backus-Naur-Form-style (BNF-style) command description syntax

| Command | Description |
|---------|-------------|
| `<command>` | Required argument  |
| `[ --optional-args ]` | Optional arguments |
| `\|` | Logical OR (mutually exclusive) |


Examples:

```bash
# argument1 is required
<argument1>

# One of argument1 or argument2 must be specified
<argument1 | argument2>

# argument1 is optional
[argument1]

# argument1 is required and argument2 is optional
<argument2> [argument1]

# If argument1 is specified, then argument2 is required
[argument1 <argument2>]
```
</details>

### 2.1 Commands

There are three commands you _can_ use but only two that you'll probably need to use.

#### 2.1.1 `start-server`

Starts a mock endpoint for you to explore uploading runs to. It is currently implemented with an API key -- if you chose to implement authentication in a different way, let me know and I'll add support for that.

```bash
shl server <start [--upload-url <upload-url>] [--upload-port <upload-port>] [-q | --quiet] [--api-key <api-key>] [--workers <num-workers>] | stop [--pid-file <pid-file>]>  
```

Minimal Example:
```bash
# Starts the demo-server at http://0.0.0.0:8000
shl server start

# Stops the demo-server -- only needed if you started the server with the `-q` flag
shl server stop
```

<details>
<summary><b>EXPAND:</b> Argument Descriptions</summary>

<table>
    <tr>
        <td>Argument</td>
        <td>Description</td>
        <td>Default</td>
    </tr>
    <tr>
        <td>--start</td>
        <td>Starts the demo-server.</td>
        <td>false</td>
    </tr>
    <tr>
        <td>--stop</td>
        <td>Stop the demo-server.</td>
        <td>false</td>
    </tr>
    <tr>
        <td>--upload-url</td>
        <td>URL or IP address of receiving server</td>
        <td>0.0.0.0</td>
    </tr>
    <tr>
        <td>--upload-port</td>
        <td>Port number of receiving server</td>
        <td>8000</td>
    </tr>
    <tr>
        <td>-q | --quiet</td>
        <td>Launch server in background and exit</td>
        <td>false</td>
    </tr>
    <tr>
        <td>--workers</td>
        <td>Number of worker processes</td>
        <td>1</td>
    </tr>
    <tr>
        <td>--pid-file</td>
        <td>File to store the process ID</td>
        <td>uvicorn.pid</td>
    </tr>
    <tr>
        <td>--api-key</td>
        <td>API key for authentication</td>
        <td>super-secret-api-key</td>
    </tr>
</table>

</details>

#### 2.1.2 `upload-run`

Uploads a log file to the specified endpoint.

```bash
shl upload-run [--run-dir <run-dir>] [--api-key <api-key>] [--upload-url <upload-url>] [--upload-port <upload-port>]
```

Minimal Example:
```bash
# Uploads example_log to the demo-server at http://0.0.0.0:8000
shl upload-run
```

<details>
<summary><b>EXPAND:</b> Argument Descriptions</summary>

<table>
    <tr>
        <td>Argument</td>
        <td>Description</td>
        <td>Default</td>
    </tr>
    <tr>
        <td>--run-dir</td>
        <td>Path to run directory</td>
        <td>example_log</td>
    </tr>
    <tr>
        <td>--api-key</td>
        <td>API key for authentication</td>
        <td>super-secret-api-key</td>
    </tr>
    <tr>
        <td>--upload-url</td>
        <td>URL or IP address of receiving server</td>
        <td>0.0.0.0</td>
    </tr>
    <tr>
        <td>--upload-port</td>
        <td>Port number of receiving server</td>
        <td>8000</td>
    </tr>
</table>

</details>


#### 2.1.3 `build-dataset-example`

Builds an example dataset from the English-German portion of the WMT14 dataset. By default, a jsonl that is 1.44GB will be created. If you want something smaller to work with, you can specify a number of samples to save (try ~1000-10,000).

```bash
shl build-dataset-example [--save-dir <save-dir>] [--num-samples <num-samples>]
```

Minimal Example:
```bash
shl build-dataset-example
```

<details>
<summary><b>EXPAND:</b> Argument Descriptions</summary>

<table>
    <tr>
        <td>Argument</td>
        <td>Description</td>
        <td>Default</td>
    </tr>
    <tr>
        <td>--save-dir</td>
        <td>Path to save the example dataset</td>
        <td>example_dataset</td>
    </tr>
    <tr>
        <td>--num-samples</td>
        <td>Number of samples to save</td>
        <td>-1</td>
    </tr>
</table>


</details>



#### 2.1.4 `train`

🚧 I'll add details here if you find you need to run the training script. 🚧


## 3. Metadata File Contents

The metadata file contains all of the information about the run. 