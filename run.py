import uvicorn
import argparse
import pathlib
import os
import sys
import importlib
import dotenv

dotenv.load_dotenv()
curent_dotenv = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(curent_dotenv):
    dotenv.load_dotenv(curent_dotenv)

parser = argparse.ArgumentParser(description="Run the FastAPI server")
parser.add_argument("--config", type=str, help="Path to the config file")

if __name__ == "__main__":
    args = parser.parse_args()
    config_path = args.config if args.config else os.environ.get("LNUVICORN_CONFIG", "")
    if config_path:
        pathObj = pathlib.Path(config_path).expanduser()
        if not pathObj.is_absolute():
            pathObj = pathlib.Path(os.getcwd(), pathObj).resolve()
        if pathObj.exists():
            sys.path.append(str(pathObj.parent))
            config = importlib.import_module(pathObj.stem)
            config = {k: v for k, v in vars(config).items() if not k.startswith("__")}
    else:
        config = {
            "host": "127.0.0.1",
            "port": 8888,
            "reload": True,
            "log_level": "debug",
        }

    if "uds" in config:
        config.pop("host", None)
        config.pop("port", None)
    uvicorn.run("app.main:app", **config)
