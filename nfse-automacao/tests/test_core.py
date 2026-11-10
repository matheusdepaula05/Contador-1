from datetime import date
from decimal import Decimal
from lxml import etree
from nfse_auto.cnpj import cnpj_valido
from nfse_auto.dps import montar_dps, id_dps, NS
from nfse_auto.models import Prestador, Tomador, Servico, Endereco, Pedido
from nfse_auto.validador import avaliar, Decisao

PREST = Prestador(cnpj="11222333000181", razao_social="Minha Empresa", ibge="3550308")
TOM = Tomador(cnpj="11444777000161", razao_social="Cliente SA",
              endereco=Endereco(logradouro="Rua A", numero="10", bairro="Centro",
                                cep="01001000", ibge="3550308", uf="SP"))
SERV = Servico(apelido="consultoria", descricao_padrao="Consultoria contábil",
               ctribnac="170101", aliquota_iss=Decimal("2.0"))


def test_cnpj():
    assert cnpj_valido("11.222.333/0001-81")
    assert not cnpj_valido("11.222.333/0001-82")
    assert not cnpj_valido("00000000000000")


def test_id_dps_tem_45_chars():
    assert len(id_dps(PREST)) == 45


def test_dps_xml():
    xml = montar_dps(PREST, TOM, SERV, Decimal("1500"), date(2026, 11, 1))
    root = etree.fromstring(xml)
    ns = {"n": NS}
    assert root.find(".//n:vServ", ns).text == "1500.00"
    assert root.find(".//n:toma/n:CNPJ", ns).text == "11444777000161"


def test_validador():
    ped = Pedido(cnpj_tomador="11444777000161", servico="consultoria", valor=Decimal("1500"))
    assert avaliar(ped, TOM, SERV, tomador_conhecido=True).decisao == Decisao.EMITIR
    assert avaliar(ped, TOM, SERV, tomador_conhecido=False).decisao == Decisao.APROVAR
    assert avaliar(ped, TOM, SERV, tomador_conhecido=True, duplicado=True).decisao == Decisao.BLOQUEAR
