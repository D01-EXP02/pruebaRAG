"""Modelos de datos tipados para el dominio de afiliados."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Afiliado(BaseModel):
    """Representa un registro de afiliado tal como está en BD_afiliados.xlsx."""

    id_afiliado: str
    tipo_documento: str
    numero_documento: str
    primer_nombre: str
    primer_apellido: str
    segundo_apellido: str
    sexo: str
    fecha_nacimiento: date
    edad: int
    ciudad: str
    departamento: str
    tipo_afiliado: str  # "Titular" | "Beneficiario"
    parentesco: Optional[str] = None
    plan: str  # "Esencial" | "Clásico" | "Premium"
    fecha_afiliacion: date
    antiguedad_meses: int
    estado_afiliacion: str  # "Activo" | "Suspendido" | "Retirado"
    estado_pagos: str  # "Al día" | "En mora"
    dias_mora: int
    valor_pendiente_cop: int
    tiene_autorizacion_previa: str  # "Sí" | "No"
    servicio_autorizado: str
    numero_autorizacion: Optional[str] = None
    fecha_autorizacion: Optional[date] = None
    vigencia_autorizacion: Optional[date] = None
    preexistencia_declarada: str  # "Sí" | "No"
    descripcion_preexistencia: str
    correo_contacto: str
    telefono_contacto: str

    @property
    def esta_activo(self) -> bool:
        return self.estado_afiliacion == "Activo"

    @property
    def esta_al_dia(self) -> bool:
        return self.estado_pagos == "Al día"

    @property
    def tiene_autorizacion_vigente(self) -> bool:
        if self.tiene_autorizacion_previa != "Sí" or self.vigencia_autorizacion is None:
            return False
        return self.vigencia_autorizacion >= date.today()