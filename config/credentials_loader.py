import json, os
from functools import lru_cache

CONFIG_FILE = os.getenv("CREDENTIALS_FILE",
                        "config_files/credentials_config.json")


@lru_cache(maxsize=1)
def _load():
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve(prj: str, field: str) -> str | None:
    """
    Return the credential <field> (github_token, taiga_user, …)
    that corresponds to <prj>. Raise KeyError if not configured.
    """
    cfg = _load()
    for course, props in cfg.items():
        if prj in props["teams"]:            

            return props.get(field)
    raise KeyError(f"Project {prj!r} not found in {CONFIG_FILE}")


