import sys

from src.app.main import create_app
from src.domain.mongo_seed_data_repository import MongoSeedDataRepository
from src.stage import Stage
from src.utils.get_env import get_env

# pylint: disable = abstract-method, import-outside-toplevel

HOST = "0.0.0.0"

if __name__ == "__main__" and "linux" in sys.platform:
    import gunicorn.app.base

    class StandaloneGunicornApplication(gunicorn.app.base.BaseApplication):

        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {}
            super().__init__()

        def load_config(self):
            config = {
                key: value
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            }

            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application


def main(*, stage: Stage = None, port: int = None):

    if stage is None:
        try:
            stage = Stage(get_env(key="STAGE"))
        except (KeyError, ValueError):
            stage = Stage.PRODUCTION

    print(stage)

    if port is None:
        try:
            port = int(get_env(key="PORT"))
        except (KeyError, ValueError):
            port = 5000

    seed_data_repo = MongoSeedDataRepository(
        url=get_env(key="MONGO_URL"),
        username=get_env(key="MONGO_USERNAME"),
        password=get_env(key="MONGO_PASSWORD"),
        db_name=get_env(key="MONGO_DB_NAME"),
        coll_name=get_env(key="MONGO_COLLECTION_NAME"),
    )

    if stage == Stage.DEV:
        import uvicorn

        app = create_app(stage=stage, seed_data_repo=seed_data_repo)

        uvicorn.run(app=app, host=HOST, port=port)

    if stage == Stage.PRODUCTION:
        try:
            options = {
                "bind": f"{HOST}:{port}",
                "workers": 1,
                "worker_class": "uvicorn.workers.UvicornWorker",
            }

            app = create_app(stage=stage, seed_data_repo=seed_data_repo)
            StandaloneGunicornApplication(app=app, options=options).run()

        except ModuleNotFoundError:
            print(f"Trying to run PROD on {sys.platform}, aborted",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
