# NFS-e Automação

Sistema para emitir NFS-e (padrão Nacional) a partir de **CNPJ do tomador + serviço + valor**.

- `docs/01-cenario-e-fluxo.md`: cenário, fluxo, squad de agentes, regras de aprovação
- `docs/02-dados-necessarios.md`: dados do tomador, prestador e catálogo de serviços
- `docs/03-arquitetura.md`: componentes, APIs, modelo de dados, segurança, roadmap, riscos
- `src/nfse_auto/`: núcleo (modelos, CNPJ, validador, gerador de DPS, esqueleto do emissor)

```
pip install -e '.[dev]' && pytest
```
Status: núcleo de validação e geração de DPS testado. **Falta** (Fase 1): assinatura XMLDSig, validação contra XSD oficial e teste em homologação com certificado A1.
