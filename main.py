import sys

from src.app.main import app as server
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

    if port is None:
        try:
            port = int(get_env(key="PORT"))
        except (KeyError, ValueError):
            port = 5000

    if stage == Stage.PRODUCTION:
        try:
            import uvicorn.workers

            options = {
                "bind": f"{HOST}:{port}",
                "workers": 4,
                "worker_class": uvicorn.workers.UvicornWorker,
            }
            StandaloneGunicornApplication(server, options).run()

        except ModuleNotFoundError:
            print(f"Trying to run PROD on {sys.platform}, defaulting to DEV",
                  file=sys.stderr)
            stage = Stage.DEV

    if stage == Stage.DEV:
        import uvicorn

        uvicorn.run(app=server, host=HOST, port=port)


if __name__ == "__main__":
    main()
