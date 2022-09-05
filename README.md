# TT2 Raid Data API

## Context

This repo is part of a bigger project concerning weekly raid data of GameHive's popular mobile game [Tap Titans 2](https://www.gamehive.com/games/tap-titans-2).

The weekly raid data for clans used to only be available on [GameHive's Discord Server](https://discord.gg/gamehive) in raw JSON format. The overarching project is an effort to make this data more accesible to players both programmatically (via API) or visually (via web app).

## Description

This API provides programmatic access to raid seed data. It supports create, retrieve and delete functionalities.

It receives data by the [TT2 Raid Info Discord Bot](https://github.com/riskypenguin/tt2-raid-info-discord-bot).

Received seeds are automatically enhanced with additional useful information.

It provides data to the [TT2 Raid Info Client](https://github.com/riskypenguin/tt2-raid-info-client).

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/riskypenguin/tt2-raid-info-api.git tt2-raid-info-api
   ```

2. Optional but recommended: Create and activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with Python version 3.9.7 or higher

3. Install requirements

   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can run the project locally via `./main.py`:

```python
python main.py
```

It tries to get `STAGE` (development / production) from the environment. Production is assumed as a default.
Note that production requires linux as `gunicorn` is not available on Windows.

You can also run the local versions directly / manually.

Dev:

```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 5000 --reload
```

Prod:

```bash
gunicorn src.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
```

## Project status & Roadmap

The API is feature-complete for now.

I am currently working on a set of refactorings to reduce coupling and improve testability.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests appropriately.

## License

[MIT](https://choosealicense.com/licenses/mit/)
