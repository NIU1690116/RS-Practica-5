import json
import os
import subprocess
import sys
from pathlib import Path

ARREL = Path(__file__).resolve().parent.parent
SCRIPT = ARREL / "src" / "tasks_app.py"


def preparar_fitxer(tmp_path, registres):
    fitxer = tmp_path / "data" / "tasks.json"
    fitxer.parent.mkdir(parents=True, exist_ok=True)
    fitxer.write_text(
        json.dumps(registres, ensure_ascii=False), encoding="utf-8"
    )
    return fitxer


def executar_cli(fitxer, *arguments):
    entorn = dict(os.environ, TASKS_DATA_FILE=str(fitxer))
    resultat = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ARREL,
        env=entorn,
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0, resultat.stderr
    return resultat.stdout.strip()


def test_gs01_creacio_correcta_duna_tasca(tmp_path):
    fitxer = preparar_fitxer(tmp_path, [])

    sortida = executar_cli(
        fitxer, "add", "--title", "Pràctica 1", "--subject", "RS"
    )

    assert sortida == "Tasca [ID: 1] creada amb èxit"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1",
            "assignatura": "RS",
            "estat": "pendent",
        }
    ]


def test_gs02_llistat_buit(tmp_path):
    fitxer = preparar_fitxer(tmp_path, [])

    sortida = executar_cli(fitxer, "list")

    assert sortida == "Registre de tasques buit."


def test_gs03_llistat_amb_registres(tmp_path):
    fitxer = preparar_fitxer(
        tmp_path,
        [
            {
                "id": 1,
                "titol": "Pràctica 1",
                "assignatura": "RS",
                "estat": "pendent",
            },
            {
                "id": 2,
                "titol": "Examen parcial",
                "assignatura": "SO",
                "estat": "pendent",
            },
        ],
    )

    sortida = executar_cli(fitxer, "list")

    assert sortida.splitlines() == [
        "[1] Pràctica 1 (RS) - estat: pendent",
        "[2] Examen parcial (SO) - estat: pendent",
    ]
