"""Montagem do XML da DPS (Declaração de Prestação de Serviços) - NFS-e Nacional.

ATENÇÃO: estrutura baseada no layout nacional (infDPS). O layout é versionado por
Notas Técnicas; valide SEMPRE contra o XSD oficial vigente (gov.br/nfse) antes de
usar em produção. Assinatura XMLDSig e envio estão em emissor.py.
"""
from __future__ import annotations
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from .models import Prestador, Tomador, Servico

NS = "http://www.sped.fazenda.gov.br/nfse"
LAYOUT_VERSAO = "1.00"
_BRT = timezone(timedelta(hours=-3))


def _m(v: Decimal) -> str:
    return str(v.quantize(Decimal("0.01"), ROUND_HALF_UP))


def id_dps(prest: Prestador) -> str:
    """'DPS' + cLocEmi(7) + tpInsc(1: CNPJ=2) + CNPJ(14) + serie(5) + nDPS(15) = 45 caracteres."""
    return f"DPS{prest.ibge}2{prest.cnpj}{int(prest.serie):05d}{prest.proximo_ndps:015d}"


def montar_dps(prest: Prestador, tom: Tomador, serv: Servico, valor: Decimal,
               competencia: date, descricao: str | None = None,
               agora: datetime | None = None) -> bytes:
    agora = agora or datetime.now(_BRT)
    E = lambda parent, tag, text=None: _el(parent, tag, text)  # noqa: E731
    root = etree.Element(f"{{{NS}}}DPS", nsmap={None: NS}, versao=LAYOUT_VERSAO)
    inf = etree.SubElement(root, f"{{{NS}}}infDPS", Id=id_dps(prest))
    E(inf, "tpAmb", str(prest.ambiente))
    E(inf, "dhEmi", agora.replace(microsecond=0).isoformat())
    E(inf, "verAplic", "nfse-auto-0.1")
    E(inf, "serie", str(int(prest.serie)))
    E(inf, "nDPS", str(prest.proximo_ndps))
    E(inf, "dCompet", competencia.isoformat())
    E(inf, "tpEmit", "1")  # 1 = prestador
    E(inf, "cLocEmi", prest.ibge)

    p = E(inf, "prest")
    E(p, "CNPJ", prest.cnpj)
    if prest.inscricao_municipal:
        E(p, "IM", prest.inscricao_municipal)
    reg = E(p, "regTrib")
    E(reg, "opSimpNac", "3" if prest.simples_nacional else "1")
    E(reg, "regEspTrib", "0")

    t = E(inf, "toma")
    E(t, "CNPJ", tom.cnpj)
    E(t, "xNome", tom.razao_social)
    if tom.endereco:
        e = E(t, "end")
        nac = E(e, "endNac")
        E(nac, "cMun", tom.endereco.ibge)
        E(nac, "CEP", tom.endereco.cep)
        E(e, "xLgr", tom.endereco.logradouro)
        E(e, "nro", tom.endereco.numero)
        E(e, "xBairro", tom.endereco.bairro)
    if tom.email:
        E(t, "email", tom.email)

    s = E(inf, "serv")
    loc = E(s, "locPrest")
    E(loc, "cLocPrestacao", prest.ibge)
    c = E(s, "cServ")
    E(c, "cTribNac", serv.ctribnac)
    E(c, "xDescServ", descricao or serv.descricao_padrao)
    if serv.nbs:
        E(c, "cNBS", serv.nbs)

    v = E(inf, "valores")
    vs = E(v, "vServPrest")
    E(vs, "vServ", _m(valor))
    tr = E(v, "trib")
    tm = E(tr, "tribMun")
    E(tm, "tribISSQN", "1")
    E(tm, "tpRetISSQN", "2" if serv.retem_iss else "1")
    if not prest.simples_nacional:
        E(tm, "pAliq", _m(serv.aliquota_iss))
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def _el(parent, tag, text=None):
    el = etree.SubElement(parent, f"{{{NS}}}{tag}")
    if text is not None:
        el.text = text
    return el
