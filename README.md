# Expt-Bimanual
#### Bimanual task replication of Schumacher et al 2018.
<mark>Linux Only</mark>

---

## Install / Run / Uninstall

### Installation

```bash
uv tool install git+https://github.com/travisseymour/exptbimanual.git
```

### Run

```bash
exptbimanual
```

### Uninstall
```bash
uv tool uninstall exptbimanual
```

---

## Development Setup

1. Clone Repository

    ```bash
    git clone https://github.com/travisseymour/exptbimanual
    cd exptbimanual
    ```

1. Create a virtual environment (Python 3.11+)

    ```bash
    python3 -m venv .venv
    ```

1. Activate virtual environment

    ```bash
    source .venv/bin/activate
    ```

1. Install project dependencies into activated virtual environment

    ```bash
    make install
    ```

1. Test Run

    ```bash
   # In PyCharm, you can also just right click on main.py and press the RUN button
    python -m exptbimanual.main
    ```

---

## Development

1. Create a branch
1. Change or add any source files
1. Stage any unstaged files you need to add to repo
1. Commit and Push
