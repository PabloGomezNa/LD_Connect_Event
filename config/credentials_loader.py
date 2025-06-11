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
            print(f"Resolving {field} for project {prj!r} in {CONFIG_FILE}")
            #Then prin the value of the field
            print(props.get(field))

                
            
            return props.get(field)
    raise KeyError(f"Project {prj!r} not found in {CONFIG_FILE}")



if __name__ == "__main__":
    # Test the credentials loader

    prj = "ASW22_Team01"
    field = "github_token"
    token = resolve(prj, field)