# shark-cli

A professional, modular CLI for the [Sharktech](https://sharktech.net) Cloud Provider API.

## Features

- **Modular architecture** — one file per resource, easily extensible.
- **Secure configuration** — env vars > YAML config file; secrets never hard-coded; config file written with `0600` permissions.
- **Rich output** — coloured tables powered by [Rich](https://github.com/Textualize/rich).
- **Shell auto-completion** — native support for Bash, Zsh, and Fish.

## Installation

```bash
# With pip (from source)
pip install .

# Or with Poetry
poetry install
```

After installation the `shark` command is available globally.

## Configuration

You need credentials from your **Sharktech Client Area** (cloud service information page):

| Field | Description | Example |
|---|---|---|
| **Auth URL** | Keystone endpoint | `https://cloud-xx.sharktech.net:5000` |
| **Username** | OpenStack user | `myuser` |
| **Password** | OpenStack password | — |
| **Domain ID** | OpenStack domain name | `mydomain` |
| **Project ID** | OpenStack project name | `myproject` |

### Option 1 — Interactive setup

```bash
shark setup
```

This prompts for all fields and stores them in `~/.shark/config.yaml` (permissions `600`).

### Option 2 — Environment variables

```bash
export SHARK_AUTH_URL="https://cloud-xx.sharktech.net:5000"
export SHARK_USERNAME="myuser"
export SHARK_PASSWORD="mypassword"
export SHARK_DOMAIN_ID="mydomain"
export SHARK_PROJECT_ID="myproject"
```

Environment variables always take precedence over the config file.

## Usage

```bash
# Show version
shark --version

# List compute servers (Nova)
shark compute list

# Show a specific server
shark compute show <server-id>

# List networks (Neutron)
shark network list
```

## Shell Auto-Completion

### Bash

Add the following line to your `~/.bashrc`:

```bash
eval "$(_SHARK_COMPLETE=bash_source shark)"
```

Then reload:

```bash
source ~/.bashrc
```

### Zsh

Add the following line to your `~/.zshrc`:

```zsh
eval "$(_SHARK_COMPLETE=zsh_source shark)"
```

Then reload:

```zsh
source ~/.zshrc
```

### Fish

```fish
_SHARK_COMPLETE=fish_source shark > ~/.config/fish/completions/shark.fish
```

You can also run `shark completion <shell>` to display these instructions at any time.

## Project Structure

```
sharktech-cli/
├── pyproject.toml                # Poetry packaging & dependencies
├── README.md
└── shark_cli/
    ├── __init__.py               # Package version
    ├── main.py                   # Click group & entry point
    ├── core/
    │   ├── client.py             # Centralised httpx API client
    │   ├── config.py             # YAML / env-var config loader
    │   ├── context.py            # Shared SharkContext object
    │   ├── exceptions.py         # Domain-specific exceptions
    │   └── validators.py         # Input validators (IDs, IPs, …)
    └── commands/
        ├── setup.py              # shark setup
        ├── compute.py            # shark compute list / show
        ├── network.py            # shark network list
        └── completion.py         # shark completion <shell>
```

## License

Apache-2.0
