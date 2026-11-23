import argparse
import json
import os
from pathlib import Path

from models import Task

DATA_FILE = Path(
    os.environ.get(
        "TASKS_DATA_FILE",
        Path(__file__).resolve().parent.parent / "data" / "tasks.json",
    )
)


def carregar_tasques():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []
    with DATA_FILE.open("r", encoding="utf-8") as fitxer:
        return [Task.from_dict(registre) for registre in json.load(fitxer)]


def desar_tasques(tasques):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as fitxer:
        json.dump(
            [tasca.to_dict() for tasca in tasques],
            fitxer,
            ensure_ascii=False,
            indent=2,
        )
        fitxer.write("\n")


def afegir_tasca(titol, assignatura):
    tasques = carregar_tasques()
    identificador = max((tasca.id for tasca in tasques), default=0) + 1
    tasques.append(Task(identificador, titol, assignatura))
    desar_tasques(tasques)
    print(f"Tasca [ID: {identificador}] creada amb èxit")


def llistar_tasques():
    tasques = carregar_tasques()
    if not tasques:
        print("Registre de tasques buit.")
        return
    for tasca in tasques:
        print(
            f"[{tasca.id}] {tasca.titol} "
            f"({tasca.assignatura}) - estat: {tasca.estat}"
        )


def construir_parser():
    parser = argparse.ArgumentParser(description="Gestor de tasques acadèmiques.")
    comandaments = parser.add_subparsers(dest="comandament", required=True)

    afegir = comandaments.add_parser("add", help="Afegeix una tasca nova")
    afegir.add_argument("--title", dest="titol", required=True, help="Títol de la tasca")
    afegir.add_argument(
        "--subject",
        dest="assignatura",
        required=True,
        help="Assignatura de la tasca",
    )

    comandaments.add_parser("list", help="Mostra totes les tasques")
    return parser


def main(argv=None):
    arguments = construir_parser().parse_args(argv)
    if arguments.comandament == "add":
        afegir_tasca(arguments.titol, arguments.assignatura)
    else:
        llistar_tasques()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
