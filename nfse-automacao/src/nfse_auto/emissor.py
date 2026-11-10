"""Assinatura e transmissão (esqueleto). Requer homologação com certificado A1.

Fluxo: DPS XML -> assinar (XMLDSig, enveloped, RSA-SHA256 sobre infDPS) ->
GZip -> Base64 -> POST na API Sefin Nacional com mTLS (certificado A1).
URLs/campos exatos: consulte a documentação técnica oficial (gov.br/nfse).
"""
from __future__ import annotations
import base64
import gzip
import httpx

URLS = {  # CONFIRMAR na documentação oficial vigente
    2: "https://sefin.producaorestrita.nfse.gov.br/SefinNacional",
    1: "https://sefin.nfse.gov.br/SefinNacional",
}


def assinar(xml: bytes, pfx_path: str, pfx_senha: str) -> bytes:
    """Assina infDPS com XMLDSig. Implementar com `signxml` + cert extraído do .pfx."""
    raise NotImplementedError("Implementar na Fase 1 com certificado de homologação")


def empacotar(xml_assinado: bytes) -> str:
    return base64.b64encode(gzip.compress(xml_assinado)).decode()


def transmitir(xml_assinado: bytes, ambiente: int, cert_pem: str, key_pem: str) -> dict:
    with httpx.Client(cert=(cert_pem, key_pem), timeout=60) as c:
        r = c.post(f"{URLS[ambiente]}/nfse", json={"dpsXmlGZipB64": empacotar(xml_assinado)})
        r.raise_for_status()
        return r.json()
