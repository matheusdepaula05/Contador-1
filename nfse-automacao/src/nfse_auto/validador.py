"""Portão de validação: decide emitir, pedir aprovação ou bloquear."""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from .cnpj import cnpj_valido
from .models import Pedido, Tomador, Servico


class Decisao(str, Enum):
    EMITIR = "emitir"
    APROVAR = "aprovacao_humana"
    BLOQUEAR = "bloquear"


@dataclass
class Resultado:
    decisao: Decisao
    motivos: list[str] = field(default_factory=list)


def avaliar(pedido: Pedido, tomador: Tomador, servico: Servico | None,
            *, tomador_conhecido: bool, teto_valor: Decimal = Decimal("10000"),
            duplicado: bool = False) -> Resultado:
    bloqueios, revisoes = [], []
    if not cnpj_valido(pedido.cnpj_tomador):
        bloqueios.append("CNPJ do tomador inválido")
    if tomador.situacao.upper() not in ("ATIVA", ""):
        bloqueios.append(f"Situação cadastral do tomador: {tomador.situacao}")
    if tomador.endereco is None:
        bloqueios.append("Tomador sem endereço/IBGE")
    if pedido.valor <= 0:
        bloqueios.append("Valor deve ser positivo")
    if duplicado:
        bloqueios.append("Possível nota duplicada (mesmo tomador/serviço/valor/competência)")
    if servico is None:
        revisoes.append("Serviço sem regra no catálogo: classificar e aprovar")
    if not tomador_conhecido:
        revisoes.append("Primeira nota para este tomador")
    if pedido.valor > teto_valor:
        revisoes.append(f"Valor acima do teto de R$ {teto_valor}")
    if bloqueios:
        return Resultado(Decisao.BLOQUEAR, bloqueios)
    if revisoes:
        return Resultado(Decisao.APROVAR, revisoes)
    return Resultado(Decisao.EMITIR)
