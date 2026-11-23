import json


class Task:
    def __init__(self, id, titol, assignatura, estat="pendent"):
        self.id = id
        self.titol = titol
        self.assignatura = assignatura
        self.estat = estat

    def to_dict(self):
        return {
            "id": self.id,
            "titol": self.titol,
            "assignatura": self.assignatura,
            "estat": self.estat,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dades):
        return cls(
            dades["id"],
            dades["titol"],
            dades["assignatura"],
            dades.get("estat", "pendent"),
        )

    @classmethod
    def from_json(cls, cadena):
        return cls.from_dict(json.loads(cadena))

    def __repr__(self):
        return (
            f"Task(id={self.id!r}, titol={self.titol!r}, "
            f"assignatura={self.assignatura!r}, estat={self.estat!r})"
        )
