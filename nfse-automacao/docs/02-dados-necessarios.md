# 2. Informações necessárias

## 2.1 Por nota: o que VOCÊ informa (mínimo)
| Campo | Exemplo | Obrigatório |
|-------|---------|-------------|
| CNPJ (ou CPF) do tomador | 12.345.678/0001-95 | Sim |
| Serviço realizado | "Consultoria contábil mensal" | Sim |
| Valor | R$ 1.500,00 | Sim |
| Competência / data da prestação | 2026-11 | Padrão = mês atual |
| Local da prestação (se diferente do prestador) | outro município | Não |
| Observações / nº pedido / contrato | "Contrato 045" | Não |

## 2.2 O que o sistema descobre sozinho do CNPJ do tomador
Razão social, nome fantasia, situação cadastral, CNAE, endereço completo (logradouro, nº, bairro, CEP, município -> **código IBGE de 7 dígitos**, UF), e-mail e telefone (quando públicos).
Fontes: BrasilAPI (gratuita), ReceitaWS, CNPJá (paga, mais estável para escala), ou consulta pela API do próprio portal nacional (CNC).

**Não vem do CNPJ e precisa ser cadastrado 1x por cliente:** e-mail de envio da nota, inscrição municipal (se houver), se é **substituto/retentor de ISS** (órgão público, empresas que retêm), regime do tomador, preferências (descrição padrão do serviço).

## 2.3 Cadastro único do PRESTADOR (configuração inicial)
- CNPJ, razão social, inscrição municipal, **código IBGE do município**
- **Regime tributário**: MEI / Simples Nacional (opção + situação) / Lucro Presumido / Real; regime especial de tributação municipal
- **Certificado digital e-CNPJ A1** (.pfx + senha) guardado em cofre de segredos
- Habilitação no **Portal NFS-e Nacional** (contribuinte cadastrado no CNC) e parametrização municipal (alíquota, serviços permitidos, benefícios)
- Série e numeração da DPS (controlada pelo sistema)
- Ambiente: homologação (produção restrita) e produção

## 2.4 Catálogo de serviços (a peça que dá escala)
Tabela que você preenche uma vez e o sistema reutiliza:

| Apelido | Descrição padrão na nota | cTribNac (6 díg.) | NBS | Alíquota ISS | Retém ISS? | Retenções federais | Local incidência |
|---------|--------------------------|-------------------|-----|--------------|-----------|--------------------|------------------|
| consultoria-contabil | Serviços de consultoria contábil ... | (da lista nacional) | (código NBS) | % do município | Não | conforme tomador | prestador |

> Os códigos exatos vêm da lista de serviços da LC 116/2003 no padrão nacional e da parametrização do seu município. **Valide com seu contador/município antes de cadastrar**: o sistema não deve "inventar" códigos.

## 2.5 Reforma Tributária (IBS/CBS)
O layout nacional incorpora grupos de **IBS/CBS** em transição (2026+). Tenha o campo previsto no modelo e acompanhe as Notas Técnicas do portal; o gerador de DPS deve ser versionado por layout.
