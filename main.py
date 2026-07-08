import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml

app = FastAPI()

# Allow CORS from anywhere (assignment requires browser access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------

def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "1", "yes", "on")

def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)

# ---------- Defaults ----------

config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# ---------- YAML ----------

if os.path.exists("config.development.yaml"):
    with open("config.development.yaml") as f:
        config.update(yaml.safe_load(f))

# ---------- .env ----------

env_file = dotenv_values(".env")

mapping = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "NUM_WORKERS": "workers",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
}

for k, v in env_file.items():
    if k in mapping:
        config[mapping[k]] = coerce(mapping[k], v)

# ---------- OS Environment ----------

for env_key, cfg_key in mapping.items():
    if env_key in os.environ:
        config[cfg_key] = coerce(cfg_key, os.environ[env_key])

# ---------- Endpoint ----------

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    result = config.copy()

    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            if k in result:
                result[k] = coerce(k, v)

    result["api_key"] = "****"

    return result
