"""Validação e consulta de CNPJ."""
from __future__ import annotations
import re
import httpx
from .models import Endereco, Tomador


def so_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def cnpj_valido(cnpj: str) -> bool:
    c = so_digitos(cnpj)
    if len(c) != 14 or len(set(c)) == 1:
        return False

    def dv(base: str) -> str:
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        if len(base) == 13:
            pesos = [6] + pesos
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        r = soma % 11
        return "0" if r < 2 else str(11 - r)

    d1 = dv(c[:12])
    d2 = dv(c[:12] + d1)
    return c[12:] == d1 + d2


def consultar_brasilapi(cnpj: str, client: httpx.Client | None = None) -> Tomador:
    c = so_digitos(cnpj)
    if not cnpj_valido(c):
        raise ValueError(f"CNPJ inválido: {cnpj}")
    http = client or httpx.Client(timeout=15)
    r = http.get(f"https://brasilapi.com.br/api/cnpj/v1/{c}")
    r.raise_for_status()
    d = r.json()
    return Tomador(
        cnpj=c,
        razao_social=d["razao_social"],
        situacao=d.get("descricao_situacao_cadastral", ""),
        email=d.get("email") or None,
        endereco=Endereco(
            logradouro=f'{d.get("descricao_tipo_de_logradouro", "")} {d["logradouro"]}'.strip(),
            numero=d.get("numero") or "S/N",
            bairro=d["bairro"],
            cep=so_digitos(d["cep"]),
            ibge=str(d["codigo_municipio_ibge"]),
            uf=d["uf"],
        ),
    )
