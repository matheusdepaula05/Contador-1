# 1. Cenário: emissão automática de NFS-e em escala

## 1.1 Premissas (confirme se estão corretas)
| # | Premissa | Se for diferente |
|---|----------|------------------|
| P1 | Você emite como **prestador** (sua empresa / empresas que você administra) e o "cliente" que você informa é o **tomador** do serviço. | Se você emite em nome de **vários prestadores** (carteira de clientes de contabilidade), o sistema precisa de multi-tenant com 1 certificado digital (ou procuração eletrônica) por prestador. A arquitetura já prevê isso (seção 3). |
| P2 | O município do prestador **aderiu ao padrão NFS-e Nacional** (portal gov.br/nfse). | Município com sistema próprio exige um adaptador de município (camada `providers/`). |
| P3 | Há certificado digital ICP-Brasil **e-CNPJ A1** do prestador (A3/token não serve para automação em nuvem). | Alternativa: autenticar via procuração + certificado do contador. |

## 1.2 O que muda com a automação
Hoje (manual): abrir portal -> consultar CNPJ -> digitar tomador -> escolher código de serviço -> descrição -> alíquota/retenções -> emitir -> baixar PDF -> enviar.

Amanhã: você manda **"CNPJ + serviço + valor"** (WhatsApp, e-mail, planilha ou formulário) e recebe de volta **PDF + XML** prontos, ou um pedido de confirmação só quando houver dúvida.

## 1.3 Fluxo ponta a ponta
```
Entrada (CNPJ + serviço + valor + competência)
   │
   ▼
[1] Agente de Intake ── interpreta texto livre -> JSON estruturado; pede o que faltar
   │
   ▼
[2] Enriquecimento do tomador ── cache no cadastro; senão consulta CNPJ (BrasilAPI/ReceitaWS/CNPJá)
   │                              razão social, endereço, código IBGE do município, situação cadastral
   ▼
[3] Agente Fiscal (motor de regras + LLM só como apoio)
   │   serviço -> cTribNac (código nacional) + NBS + alíquota ISS + retenções + local de incidência
   │   regra determinística primeiro; LLM sugere apenas quando não há regra, e isso VAI PARA REVISÃO
   ▼
[4] Validador ── CNPJ ativo? município do tomador? valores? limites MEI/Simples? duplicidade?
   │             XSD do layout nacional
   ▼
[5] Portão de aprovação (configurável) ── auto-emitir | pedir OK humano (regras abaixo)
   ▼
[6] Emissor ── monta DPS XML -> assina (XMLDSig, cert A1) -> POST na API Sefin Nacional (mTLS)
   │            recebe NFS-e (chave de acesso de 50 dígitos) ou erro
   ▼
[7] Pós-emissão ── guarda XML, baixa DANFSe (PDF), registra no banco, envia ao cliente (e-mail/WhatsApp)
   │               atualiza planilha/ERP/financeiro
   ▼
[8] Observabilidade ── fila de erros, reprocessamento, relatório mensal, cancelamento/substituição
```

## 1.4 Regra de ouro: quando emitir sozinho x pedir confirmação
Fiscal não perdoa erro (cancelar NFS-e tem prazo e custo). Política sugerida:

| Situação | Ação |
|----------|------|
| Tomador já conhecido + serviço já mapeado + valor dentro do histórico (±30%) | **Emite automático** |
| Tomador novo (1ª nota) | Pede OK humano 1x; depois vira "conhecido" |
| Serviço sem regra cadastrada | Agente sugere classificação -> **OK humano** -> vira regra |
| Valor acima do teto configurado / divergência de histórico | OK humano |
| CNPJ do tomador baixado/inapto/suspenso | **Bloqueia** e avisa |
| Retenção de ISS/IR/PCC incerta | OK humano |
| Possível duplicidade (mesmo tomador+serviço+valor+competência) | Bloqueia |

Com o uso, quase tudo vira "automático" porque o cadastro de regras amadurece.

## 1.5 Esquadrão (squad) de agentes
| Agente | Função | Usa LLM? |
|--------|--------|----------|
| **Intake** | Lê mensagem/planilha/áudio transcrito, extrai CNPJ, serviço, valor, data, parcelas | Sim |
| **Cadastro** | Consulta/atualiza dados do tomador (CNPJ -> endereço/IBGE) | Não (APIs) |
| **Fiscal** | Classifica serviço (cTribNac/NBS), alíquota, retenções | Regras + LLM como sugestão |
| **Compliance/Validação** | Valida XSD, CNPJ, duplicidade, limites | Não |
| **Emissor** | Assina e transmite; trata retorno e rejeições | Não |
| **Entrega** | PDF/XML, e-mail/WhatsApp, baixa no financeiro | Não (template) |
| **Supervisor** | Orquestra, decide aprovação, escala exceções para você | Sim (leve) |

> Princípio: **LLM entende e sugere; código determinístico decide e emite.** Nunca deixe o modelo preencher campo fiscal sem regra ou sem sua revisão na 1ª vez.
