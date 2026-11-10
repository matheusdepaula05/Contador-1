# 3. Engenharia ponta a ponta

## 3.1 Visão de componentes
```
 Canais de entrada                 Núcleo (API + workers)                       Externos
┌──────────────────┐   ┌──────────────────────────────────────────┐   ┌─────────────────────────┐
│ WhatsApp/Telegram│   │ API FastAPI  /pedidos  /aprovacoes       │   │ API NFS-e Nacional      │
│ E-mail (IMAP)    │──▶│   │                                      │──▶│ (Sefin Nacional, mTLS)  │
│ Planilha Sheets  │   │   ▼ fila (Redis/RQ ou Celery)            │   │ ADN / CNC / parâmetros  │
│ Formulário web   │   │ Orquestrador (Supervisor)                │   ├─────────────────────────┤
└──────────────────┘   │  ├ Intake  ├ Cadastro ├ Fiscal           │──▶│ BrasilAPI/ReceitaWS/    │
                       │  ├ Validador ├ Emissor ├ Entrega          │   │ CNPJá (consulta CNPJ)   │
 Painel (aprovar,      │  └ Auditoria                              │   ├─────────────────────────┤
 revisar, relatórios)  │ PostgreSQL | Object storage (XML/PDF)     │──▶│ LLM (Claude API)        │
└─ Next.js / Retool    │ Cofre de segredos (certificados A1)       │   │ Gmail/WhatsApp/ERP      │
                       └──────────────────────────────────────────┘   └─────────────────────────┘
```

## 3.2 APIs e integrações
| Função | API | Observações |
|--------|-----|-------------|
| Emitir NFS-e | **Sefin Nacional** (REST, `POST /nfse` com DPS assinada, GZip+Base64) | Autenticação **mTLS** com e-CNPJ A1. Há ambiente de **produção restrita** (homologação) |
| Consultar/baixar NFS-e, eventos (cancelar, substituir) | Sefin Nacional / **ADN** | Cancelamento é um *evento* assinado |
| Parâmetros do município (alíquotas, serviços, convênio) | API de **parametrização municipal** | Cachear e atualizar periodicamente |
| PDF (DANFSe) | Serviço de DANFSe do portal | Fallback: gerar PDF próprio a partir do XML |
| Dados do CNPJ | BrasilAPI (grátis) -> CNPJá/ReceitaWS (escala) | Cache de 30 dias; fallback em cascata |
| IA | Claude API | Intake e sugestão de classificação fiscal |
| Entrega | SMTP/Gmail API, WhatsApp Business API | Template fixo, sem IA |
| Financeiro (opcional) | Conta Azul/Omie/Bling/Sheets | Baixa/lançamento automático |

> **Confirme as URLs e o layout vigente** na documentação oficial (gov.br/nfse -> "Documentação Técnica": APIs, XSDs, Notas Técnicas). O layout muda por Nota Técnica; por isso o gerador é versionado (`LAYOUT_VERSAO`).

## 3.3 Modelo de dados (PostgreSQL)
- `prestadores` (id, cnpj, razao, im, ibge, regime, cert_ref, serie, proximo_ndps, ambiente)
- `tomadores` (id, cnpj/cpf, razao, endereco_json, ibge, email_envio, retentor_iss, atualizado_em)
- `servicos` (id, prestador_id, apelido, descricao_padrao, ctribnac, nbs, aliquota, retem_iss, ...)
- `pedidos` (id, origem, texto_bruto, json_extraido, status, motivo_bloqueio, criado_por)
- `notas` (id, pedido_id, ndps, chave_acesso, xml_dps, xml_nfse, pdf_url, status, protocolo, emitida_em)
- `aprovacoes`, `eventos_fiscais` (cancelamentos), `auditoria` (quem/quando/o quê, imutável)

Status do pedido: `recebido -> interpretado -> enriquecido -> classificado -> validado -> aguardando_aprovacao -> emitindo -> emitida | rejeitada | bloqueada`.

## 3.4 Segurança e conformidade (inegociável)
- Certificado A1 e senha em **cofre** (AWS Secrets Manager / GCP Secret Manager / Vault); nunca no repositório ou em `.env` commitado.
- Idempotência: `ndps` reservado em transação + chave de idempotência por pedido (evita nota duplicada em retry).
- Trilha de auditoria imutável; XML original guardado por **5 anos** (guarda fiscal).
- LGPD: dados de tomadores mínimos, acesso por papel, logs sem dados sensíveis.
- Limites de segurança: teto de valor por nota, teto diário, aprovação humana acima do teto.
- Rejeições da SEFIN mapeadas para ações (corrigir e reenviar, ou escalar ao humano).

## 3.5 Stack recomendada
Python 3.12 · FastAPI · PostgreSQL · Redis + RQ · `lxml` + `signxml` (XMLDSig) · `httpx` (mTLS) · Pydantic · Docker · deploy em Cloud Run/Fly/AWS ECS · painel em Next.js ou Retool · Claude API para Intake/Fiscal.

## 3.6 Roadmap
| Fase | Entrega | Prazo estimado |
|------|---------|----------------|
| 0 | Levantar: certificado A1, adesão do município, catálogo de serviços, 20 notas reais como base de teste | 1 sem |
| 1 | **MVP**: formulário/planilha -> consulta CNPJ -> DPS -> **homologação** -> PDF/XML (tudo com OK humano) | 2-3 sem |
| 2 | Produção com aprovação humana + entrega por e-mail + cadastro de tomadores/serviços | 2 sem |
| 3 | Intake em linguagem natural (WhatsApp/e-mail) + regras de auto-emissão | 2-3 sem |
| 4 | Multi-prestador, cancelamento/substituição, financeiro, relatórios, painel | 3-4 sem |

## 3.7 Riscos
1. **Layout/regras mudam** (Reforma Tributária) -> gerador versionado + testes contra XSD oficial.
2. **Município fora do padrão nacional** -> camada de adaptadores.
3. **Classificação fiscal errada** -> regra determinística + revisão humana na 1ª vez.
4. **Instabilidade da API do governo** -> fila com retry/backoff e emissão assíncrona.
5. **Responsabilidade fiscal permanece sua**: o sistema automatiza, mas valide o catálogo com o contador.
