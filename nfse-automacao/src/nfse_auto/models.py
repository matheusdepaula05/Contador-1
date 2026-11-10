"""Modelos de domínio (entrada do usuário -> DPS)."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class Endereco(BaseModel):
    logradouro: str
    numero: str = "S/N"
    bairro: str
    cep: str
    ibge: str = Field(min_length=7, max_length=7)  # código do município (7 dígitos)
    uf: str


class Tomador(BaseModel):
    cnpj: str
    razao_social: str
    situacao: str = "ATIVA"
    endereco: Endereco | None = None
    email: str | None = None
    retentor_iss: bool = False


class Prestador(BaseModel):
    cnpj: str
    razao_social: str
    inscricao_municipal: str | None = None
    ibge: str
    simples_nacional: bool = True  # opSimpNac
    serie: str = "1"
    proximo_ndps: int = 1
    ambiente: int = 2  # 1=produção, 2=homologação


class Servico(BaseModel):
    apelido: str
    descricao_padrao: str
    ctribnac: str = Field(min_length=6, max_length=6)  # código de tributação nacional
    nbs: str | None = None
    aliquota_iss: Decimal  # %
    retem_iss: bool = False


class Pedido(BaseModel):
    """O que o usuário informa: CNPJ + serviço + valor."""
    cnpj_tomador: str
    servico: str  # apelido do catálogo
    valor: Decimal
    competencia: date | None = None
    observacao: str | None = None
