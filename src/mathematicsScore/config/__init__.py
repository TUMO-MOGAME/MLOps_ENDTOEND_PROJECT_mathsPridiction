from pathlib import Path

CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("params.yaml")

print(f"Config file path: {CONFIG_FILE_PATH.resolve()}")
print(f"Params file path: {PARAMS_FILE_PATH.resolve()}")