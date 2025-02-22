# Software Hut Logger

A package containing the logger demo for Software Hut using Hugging Face 🤗 Transformers Trainer.

`NOTE:` This is intended to be used with linux systems. If you are using Windows, you should use WSL2 for everything related to this package.

## Installation & Setup

```bash
# Create a virtual environment
python3 -m venv shl-demo-venv
source shl-demo-venv/bin/activate
pip install software-hut-logger
```

`NOTE:` If you want to edit the code or rerun the training script for any reason, let me know and I'll add instructions.


## Usage

If installed correctly, the package should be available as a command-line tool. 

```bash
# Both commands are equivalent
shl <command> [ --project-name <project-name> ] [ --experiment-name <experiment-name> ] [ --run-name <run-name> ] [...command-specific-options]

software-hut-logger <command> [ --project-name <project-name> ] [ --experiment-name <experiment-name> ] [ --run-name <run-name> ] [...command-specific-options]
```

`NOTE:` Anywhere that "-" is used in an argument name, "_" is also valid.

<details>
<summary><b>EXPAND:</b> What the hell is this command description syntax?</summary>

### Backus-Naur-Form-style (BNF-style) command description syntax

| Command | Description |
|---------|-------------|
| `<command>` | Required argument  |
| `[ --optional-args ]` | Optional arguments |
| `\|` | Logical OR (mutually exclusive) |


#### Examples

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

### Commands

There are three commands you _can_ use but only two that you'll probably need to use.

#### `start-server`

Starts a mock endpoint for you to explore uploading runs to. It is currently implemented with an API key -- if you chose to implement authentication in a different way, let me know and I'll add support for that.

```bash
shl server <start [--upload-url <upload-url>] [--upload-port <upload-port>] [-q | --quiet] [--api-key <api-key>] [--workers <num-workers>] | stop [--pid-file <pid-file>]>  
```

Minimal Example:
```bash
# Starts the demo-server at http://0.0.0.0:8000
shl server start

# Stops the demo-server
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

#### `upload-log`

Uploads a log file to the specified endpoint.

```bash
shl upload-log [--run-dir <run-dir>] [--api-key <api-key>] [--upload-url <upload-url>] [--upload-port <upload-port>]
```

Minimal Example:
```bash
# Uploads example_log to the demo-server at http://0.0.0.0:8000
shl upload-log
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


#### `train`

🚧 I'll add details here if you find you need to run the training script. 🚧


## Metadata File Contents

The metadata file contains all of the information about the run. 