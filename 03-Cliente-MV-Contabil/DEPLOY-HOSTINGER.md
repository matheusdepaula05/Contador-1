# Guia de Publicação — Página MV Contábil na Hostinger (WordPress)

Sua hospedagem Hostinger roda WordPress. A boa notícia: **você não precisa mexer no WordPress nem no Elementor.**
A página é um arquivo HTML único e independente — sobe numa **subpasta** e o WordPress não interfere.

---

## Por que a subpasta funciona (mesmo com WordPress)

O `.htaccess` padrão do WordPress só redireciona para o `index.php` aquilo que **não existe** como arquivo ou pasta real:

```apache
RewriteCond %{REQUEST_FILENAME} !-f   # se NÃO for um arquivo existente
RewriteCond %{REQUEST_FILENAME} !-d   # e NÃO for uma pasta existente
RewriteRule . /index.php [L]          # aí sim manda pro WordPress
```

Como `/demo-mv/` é uma **pasta real** com um `index.html` **real**, o Apache serve direto — o WordPress nem vê. Zero conflito.

---

## MÉTODO RECOMENDADO — Subpasta via hPanel (5 minutos)

### Arquivos que você vai subir
Estão em `mv-contabil-deploy.zip`:
- `index.html` — a página
- `favicon.svg` — ícone da aba
- `og-image.png` — imagem que aparece ao compartilhar o link

### Passo a passo
1. Entre na **Hostinger → hPanel** do seu domínio.
2. Abra **Arquivos → Gerenciador de Arquivos**.
3. Entre na pasta **`public_html`** (onde está o WordPress).
4. Clique em **Nova Pasta** e crie: **`demo-mv`**.
5. Entre na pasta `demo-mv` e clique em **Enviar (Upload) → Arquivo**. Suba o **`mv-contabil-deploy.zip`**.
6. Clique com o botão direito no zip → **Extrair (Extract)**. Os 3 arquivos aparecem soltos na pasta.
7. (Opcional) Apague o `.zip` depois de extrair.
8. Pronto. Acesse no navegador:
   ```
   https://SEUDOMINIO.com/demo-mv/
   ```

> **URL mais bonita (opcional):** se quiser `demo-mv.seudominio.com` em vez de `/demo-mv/`, vá em **hPanel → Domínios → Subdomínios**, crie o subdomínio `demo-mv` e aponte a pasta-raiz dele para `public_html/demo-mv`.

---

## ANTES DE ENVIAR PARA A MV — ajustes de 2 minutos

Abra o `index.html` (no Gerenciador de Arquivos: botão direito → **Editar**) e troque:

| Procure por | Troque por | Onde |
|---|---|---|
| `SEU-DOMINIO/demo-mv/` | seu endereço real (ex.: `suaagencia.com/demo-mv/`) | aparece em 4 tags `og:`/`canonical`/JSON-LD |
| `[seu número]` *(no PDF, não no site)* | seu WhatsApp | peça de venda |

**Quando a página virar o site OFICIAL da MV** (no domínio dela), faça 1 troca a mais:
```html
<!-- de: -->
<meta name="robots" content="noindex, nofollow" />
<!-- para: -->
<meta name="robots" content="index, follow" />
```
Isso libera o Google para indexar. Enquanto for **demonstração no seu domínio**, deixe `noindex` (evita que a demo seja achada/confundida com o site real).

**Confirmar com a MV antes de indexar:** CEP (`06010-040` foi inferido) e horário no bloco de SEO (JSON-LD, final do arquivo).

---

## O que já vem pronto nesta versão de produção
- **Favicon** com a logomarca da MV na aba do navegador.
- **SEO local (JSON-LD `AccountingService`)** — nome, endereço, telefone, horário e Instagram estruturados para o Google entender que é contabilidade em Osasco. *(É a base do "encontrável no Google" — sem prometer 1ª posição.)*
- **Card de compartilhamento (Open Graph + Twitter)** — ao mandar o link no WhatsApp/Instagram, aparece a imagem `og-image.png` com a marca.
- **`noindex` de demonstração** — seguro para mostrar antes de publicar oficialmente.
- **Performance**: CSS/JS embutidos, ícones em vetor, fontes carregadas sem travar a tela. Zero erro de console.

---

## ALTERNATIVA — como página dentro do WordPress (se você fizer questão)

Só vale se você quiser gerenciar a página pelo painel do WP. **Perde parte do movimento e dá mais trabalho** — por isso a subpasta acima é melhor.

1. Instale o tema/recurso **Elementor**.
2. Crie uma **Página** nova → em *Configurações da Página* escolha o template **"Tela Cheia / Canvas"** (sem cabeçalho e rodapé do tema).
3. Adicione um widget **HTML** e cole o conteúdo do `<body>` (sem as tags `<html>`/`<head>`). O CSS e o JS embutidos vão junto.
4. As fontes do Google e o mapa continuam funcionando. Publique.

> Observação: alguns recursos (favicon, JSON-LD no `<head>`, tags Open Graph) precisam ser adicionados por um plugin de SEO (ex.: Rank Math/Yoast) ou em "Inserir cabeçalho e rodapé", porque o widget HTML não escreve no `<head>`. Por isso a **subpasta entrega tudo pronto de uma vez**.

---

## Resumo
- **Mais simples e completo:** subir o `.zip` em `public_html/demo-mv/` e extrair → `seudominio.com/demo-mv/`.
- WordPress fica intacto. Movimento, SEO, favicon e card de compartilhamento já inclusos.
- Trocar `SEU-DOMINIO` antes de divulgar; trocar `noindex→index` só quando for o site oficial da MV.

---
*Arsenal de Funis — © 7D/SECRETS LTDA (Anthony Nichols & André Cia)*
