import json
import os
import subprocess
import sys
from pathlib import Path

ARREL = Path(__file__).resolve().parent.parent
SCRIPT = ARREL / "src" / "tasks_app.py"


def ruta_dades(tmp_path):
    return tmp_path / "data" / "tasks.json"


def preparar_fitxer(tmp_path, registres):
    fitxer = ruta_dades(tmp_path)
    fitxer.parent.mkdir(parents=True, exist_ok=True)
    fitxer.write_text(
        json.dumps(registres, ensure_ascii=False), encoding="utf-8"
    )
    return fitxer


def executar_cli(fitxer, *arguments):
    entorn = dict(os.environ, TASKS_DATA_FILE=str(fitxer))
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ARREL,
        env=entorn,
        capture_output=True,
        text=True,
    )


def tasca(identificador, titol, assignatura):
    return {
        "id": identificador,
        "titol": titol,
        "assignatura": assignatura,
        "estat": "pendent",
    }


def test_gs01_creacio_correcta_duna_tasca(tmp_path):
    fitxer = preparar_fitxer(tmp_path, [])

    resultat = executar_cli(
        fitxer, "add", "--title", "Pràctica 1", "--subject", "RS"
    )

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip() == "Tasca [ID: 1] creada amb èxit"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        tasca(1, "Pràctica 1", "RS")
    ]


def test_gs02_llistat_buit(tmp_path):
    fitxer = preparar_fitxer(tmp_path, [])

    resultat = executar_cli(fitxer, "list")

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip() == "Registre de tasques buit."


def test_gs03_llistat_amb_registres(tmp_path):
    fitxer = preparar_fitxer(
        tmp_path,
        [tasca(1, "Pràctica 1", "RS"), tasca(2, "Examen parcial", "SO")],
    )

    resultat = executar_cli(fitxer, "list")

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip().splitlines() == [
        "[1] Pràctica 1 (RS) - estat: pendent",
        "[2] Examen parcial (SO) - estat: pendent",
    ]


def test_gs04_creacio_automatica_del_fitxer_json(tmp_path):
    fitxer = ruta_dades(tmp_path)
    assert not fitxer.exists()

    resultat = executar_cli(fitxer, "list")

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip() == "Registre de tasques buit."
    assert fitxer.exists()
    assert fitxer.read_text(encoding="utf-8").strip() == "[]"


def test_gs05_assignacio_incremental_d_id(tmp_path):
    primer = tasca(1, "Pràctica 1", "RS")
    fitxer = preparar_fitxer(tmp_path, [primer])

    resultat = executar_cli(
        fitxer, "add", "--title", "Laboratori 2", "--subject", "BD"
    )

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip() == "Tasca [ID: 2] creada amb èxit"
    assert json.loads(fitxer.read_text(encoding="utf-8")) == [
        primer,
        tasca(2, "Laboratori 2", "BD"),
    ]


def test_gs06_nou_id_quan_el_mes_alt_no_es_correlatiu(tmp_path):
    fitxer = preparar_fitxer(
        tmp_path, [tasca(1, "Pràctica 1", "RS"), tasca(5, "Examen", "SO")]
    )

    resultat = executar_cli(
        fitxer, "add", "--title", "Treball final", "--subject", "PW"
    )

    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.strip() == "Tasca [ID: 6] creada amb èxit"
    assert json.loads(fitxer.read_text(encoding="utf-8"))[-1] == tasca(
        6, "Treball final", "PW"
    )


def test_gs07_error_sense_arguments_obligatoris(tmp_path):
    registre = [tasca(1, "Pràctica 1", "RS")]
    fitxer = preparar_fitxer(tmp_path, registre)
    contingut = fitxer.read_text(encoding="utf-8")

    resultat = executar_cli(
        fitxer, "add", "--title", "Pràctica sense assignatura"
    )

    assert resultat.returncode != 0
    assert resultat.stderr.strip()
    assert fitxer.read_text(encoding="utf-8") == contingut


def test_gs08_fitxer_json_mal_format(tmp_path):
    fitxer = ruta_dades(tmp_path)
    fitxer.parent.mkdir(parents=True, exist_ok=True)
    fitxer.write_text("{json_invalid", encoding="utf-8")

    resultat = executar_cli(fitxer, "list")

    assert resultat.returncode != 0
    assert "json" in resultat.stderr.lower()
    assert fitxer.read_text(encoding="utf-8") == "{json_invalid"
