"""Acceso de solo lectura a la base de datos de afiliados (Excel)."""
from pathlib import Path
from typing import Optional

import pandas as pd

from .modelos import Afiliado

COLUMNAS_OPCIONALES = [
    "parentesco",
    "numero_autorizacion",
    "fecha_autorizacion",
    "vigencia_autorizacion",
]


class AfiliadoNoEncontradoError(Exception):
    """Se lanza cuando no existe n afiliado con el id solicitado."""


class AfiliadosRepository:
    def __init__(self, ruta_excel: str | Path):
        self._ruta = Path(ruta_excel)
        if not self._ruta.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {self._ruta}")

        df = pd.read_excel(self._ruta, sheet_name="Afiliados")
        df = df.astype({"numero_documento": str, "telefono_contacto": str})

        for columna in COLUMNAS_OPCIONALES:
            df[columna] = df[columna].astype(object)
            df[columna] = df[columna].where(df[columna].notna(), None)

        self._df = df.set_index("id_afiliado", drop=False)

    def buscar_por_id(self, id_afiliado: str) -> Optional[Afiliado]:
        """Devuelve el afiliado o None si no existe."""
        if id_afiliado not in self._df.index:
            return None
        fila = self._df.loc[id_afiliado].to_dict()
        return Afiliado(**fila)

    def obtener_o_lanzar(self, id_afiliado: str) -> Afiliado:
        """Igual que buscar_por_id, pero lanza excepción si no existe."""
        afiliado = self.buscar_por_id(id_afiliado)
        if afiliado is None:
            raise AfiliadoNoEncontradoError(
                f"No existe un afiliado con id '{id_afiliado}'"
            )
        return afiliado