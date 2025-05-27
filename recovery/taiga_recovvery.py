#!/usr/bin/env python
"""
Bulk back‑fill de eventos GitHub y Taiga hacia Mongo
uso:
    ld_backfill github --org ORG --repo REPO --prj TEAM42
    ld_backfill taiga  --url https://taiga.upc.edu --project-id 123 --token ABC --prj TEAM42
"""
import json, os, time, logging, datetime, itertools, re
from typing import Dict, Iterable, List, Any, Optional

import click, requests, pymongo
from dateutil import parser as dtp
from tqdm import tqdm

# ──────────────────────────────────────────────────────────────────────────────
#  CONFIG GLOBAL                                                              │
# ──────────────────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "ld_connect")

GITHUB_TOKEN   = os.getenv("GH_TOKEN")
TAIGA_TOKEN    = os.getenv("TAIGA_TOKEN")          # se puede sobreescribir en CLI
TAIGA_BASE_URL = os.getenv("TAIGA_BASE_URL")

LD_EVAL_URL    = os.getenv("LD_EVAL_URL")          # p.e. http://localhost:8000/recalc

client = pymongo.MongoClient(MONGO_URI)
db     = client[MONGO_DB]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("ld_backfill")

# ──────────────────────────────────────────────────────────────────────────────
#  UTILIDADES COMUNES                                                         │
# ──────────────────────────────────────────────────────────────────────────────
def upsert_many(coll, docs: List[Dict], key: str):
    """Inserta o actualiza muchos documentos de golpe usando `key` como PK."""
    if not docs:
        return
    ops = []
    for d in docs:
        ops.append(pymongo.UpdateOne({key: d[key]}, {"$set": d}, upsert=True))
    coll.bulk_write(ops, ordered=False)

def fake_request_headers(event_name: str) -> Dict[str, str]:
    """Genera las cabeceras que normalmente manda GitHub/Taiga al webhook."""
    return {"X-GitHub-Event": event_name}


# ──────────────────────────────────────────────────────────────────────────────
#  TAIGA BACK‑FILL                                                            │
# ──────────────────────────────────────────────────────────────────────────────
def taiga_paginated(endpoint: str, headers: Dict[str, str], key=""):
    """Taiga usa paginación con ‘next’ en JSON. Devuelve items de todas las páginas."""
    while endpoint:
        r = requests.get(endpoint, headers=headers)
        r.raise_for_status()
        data = r.json()
        if key:                   # /history devoluciones distintas
            yield from data[key]
        else:
            yield from data
        endpoint = (data if isinstance(data, dict) else {}).get("next")

def collect_taiga(base_url: str, project_id: int, token: str, prj: str) -> None:
    """Descarga user‑stories, tasks, issues, history de un proyecto Taiga."""
    from datasources.taiga_handler import parse_taiga_event   # debes crearlo o adaptar el tuyo

    headers = {"Authorization": f"Bearer {token}"}
    coll_suffix = f"taiga_{prj}"

    endpoints = {
        "userstories": f"{base_url}/api/v1/userstories?project={project_id}",
        "tasks":       f"{base_url}/api/v1/tasks?project={project_id}",
        "issues":      f"{base_url}/api/v1/issues?project={project_id}",
    }

    total = 0
    for etype, url in endpoints.items():
        log.info("Descargando %s…", etype)
        for item in tqdm(list(taiga_paginated(url, headers)), desc=etype, unit="obj"):
            fake_payload = {"event": etype, "data": item, "prj": prj}
            parsed = parse_taiga_event(fake_payload)   #  implementa o usa tu parser actual
            if parsed.get("ignored"):
                continue
            coll = db[f"{coll_suffix}.{etype}"]
            key = "id"  # los objetos Taiga tienen id único
            upsert_many(coll, [parsed], key)
            total += 1
    log.info("Taiga back‑fill terminado: %s documentos grabados", total)

# ──────────────────────────────────────────────────────────────────────────────
#  MÉTRICAS LD‑EVAL                                                           │
# ──────────────────────────────────────────────────────────────────────────────
def trigger_ld_eval(prj: str):
    if not LD_EVAL_URL:
        log.warning("LD_EVAL_URL no configurado; omito recálculo de métricas.")
        return
    url = f"{LD_EVAL_URL}?prj={prj}"
    log.info("Invocando LD‑Eval: %s", url)
    r = requests.post(url)
    if r.ok:
        log.info("Métricas recalculadas con éxito.")
    else:
        log.error("LD‑Eval devolvió %s ‑ %s", r.status_code, r.text)

# ──────────────────────────────────────────────────────────────────────────────
#  CLI                                                                       │
# ──────────────────────────────────────────────────────────────────────────────
@click.group()
def cli():
    """Herramienta de back‑fill para LD‑Connect."""
    pass

@cli.command()
@click.option("--org",  required=True, help="GitHub organization / owner")
@click.option("--repo", required=True, help="GitHub repository name")
@click.option("--prj",  required=True, help="ID de equipo (colección Mongo)")
@click.option("--recalc/--no-recalc", default=True,
              help="Lanzar recálculo de métricas al terminar")
def github(org, repo, prj, recalc):
    """Back‑fill completo desde GitHub REST API."""
    collect_github(org, repo, prj)
    if recalc:
        trigger_ld_eval(prj)

@cli.command()
@click.option("--url",        default=TAIGA_BASE_URL, help="Base URL de Taiga")
@click.option("--project-id", type=int, required=True, help="ID numérico de proyecto")
@click.option("--token",      default=TAIGA_TOKEN,    help="Taiga bearer token")
@click.option("--prj",        required=True, help="ID de equipo (colección Mongo)")
@click.option("--recalc/--no-recalc", default=True,
              help="Lanzar recálculo de métricas al terminar")
def taiga(url, project_id, token, prj, recalc):
    """Back‑fill completo desde Taiga API v1."""
    if not token:
        raise click.ClickException("Necesitas --token o variable TAIGA_TOKEN")
    collect_taiga(url, project_id, token, prj)
    if recalc:
        trigger_ld_eval(prj)

if __name__ == "__main__":
    cli()
