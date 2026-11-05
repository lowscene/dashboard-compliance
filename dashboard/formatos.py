"""Formatação de números no padrão pt-BR (vírgula decimal, ponto de milhar)."""
from __future__ import annotations

import pandas as pd

AUSENTE = "—"


def num(valor: float, casas: int = 0) -> str:
    """1234.5 -> '1.234,5' (com as casas pedidas)."""
    if pd.isna(valor):
        return AUSENTE
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def curto(valor: float) -> str:
    """Número sem zeros à direita: 5.0 -> '5', 0.5 -> '0,5'."""
    if pd.isna(valor):
        return AUSENTE
    return f"{valor:g}".replace(".", ",")


def pct(valor: float, casas: int = 1) -> str:
    """Fração em percentual: 0.9346 -> '93,5%'."""
    if pd.isna(valor):
        return AUSENTE
    return num(valor * 100, casas) + "%"


def pct_curto(valor: float) -> str:
    """Fração em percentual sem zeros à direita: 0.9 -> '90%'."""
    if pd.isna(valor):
        return AUSENTE
    return curto(valor * 100) + "%"


def dias(valor: float, casas: int = 2) -> str:
    if pd.isna(valor):
        return AUSENTE
    return num(valor, casas) + " dias"
