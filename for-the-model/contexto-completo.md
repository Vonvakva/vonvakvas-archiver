# Contexto Completo do Projeto — Vonvakva's Archive

**Gerado em:** 30/08/2026
**Versão:** 1.0
**Natureza:** Documento de contexto para modelos de IA. Contém TODO o estado atual do projeto para que qualquer modelo consiga trabalhar nele sem precisar explorar do zero.

---

## 1. O que é o projeto

**Vonvakva's Archive** é um sistema pessoal, em **Bash**, para **arquivamento/preservação de canais do YouTube** (foco em canais de ASMR, que costumam cair/desaparecer). O pipeline completo é:

1. **Download** em massa de canais via `yt-dlp` (com rotação de cookies de 3 contas para evitar bloqueio do YouTube).
2. **Organização** automática dos arquivos em subpastas por tipo.
3. **Upload** para o **Internet Archive** (preservação permanente).
4. **Monitoramento** de canais (detecção de canal offline/caído) com **alerta via Telegram**.

O nome da pasta-mãe é **`archiveguiprep`** = "GUI prep". O objetivo do projeto é preparar o backend para construir uma **interface gráfica (GUI)** futura. O arquivo `vonvakvas.sh` na raiz é a **API** que a GUI vai chamar nos botões.

---

## 2. Lore (de `lore.txt`)

Explicações do autor sobre os scripts ("por quê"):

| Nome | Explicação |
|---|---|
| `nts` | Abreviação de **"no time-space"**. Criado durante a parte 4 de JoJo; obcecado pelo **ZA HANDO** (poder de apagar espaço-tempo). Sonho físico futuro: homelab com HDDs e servidor para infraestrutura de archiving mais bruta. |
| `ntsp` | Variante mais agressiva (na opinião do autor) do nts; baixa vídeos com cookies "live" (do navegador) e resolvedores de challenges com impersonate. |
| `organizeri` | Organizer **Instagram** (pretende arquivar Instagram no futuro). |
| `organizerm` | Organizer de **músicas** (já utilizado de fato). |
| `desorganizar` | Criado na época de testes do organizador principal. |
| Por que o organizer é tão "bloatado"? | Autor não domina shell nem encurtadores; queria "animaçãozinha" → poluição visual proposital (:sob:) |
| `uploaderf` | Uploader **full** — escrito em partes e juntado até terminar. Sonho: o item ir pro **mirrortube**, sentindo-se pertencido à comunidade. |
| `organizerv2` | Versão 2 do organizer: **prepara a pasta para upload** no Internet Archive. |

---

## 3. Regras do projeto (de `for-the-model/agentrules.md`)

- Não mover scripts sem atualizar suas referências.
- Não assumir que o working directory é o diretório atual (`pwd`).
- Caminhos devem ser derivados do diretório do projeto.
- **Não substituir Bash por outra linguagem sem necessidade.**
- Preservar a estrutura existente do backend.
- Antes de alterar um script, verificar quais outros scripts o chamam.
- Não remover funcionalidades existentes durante refatorações.
- Preferir alterações pequenas e testáveis.
- **Regras da GUI:** analisar a pasta, ler cada arquivo, gerar plano de ação antes de implementar; o `vonvakvas.sh` é a API para os botões da GUI; pode ajustar/adicionar comandos nela.
- **Regra geral nova:** evitar usar `/tmp` (RAM de 8GB — enche rápido e é sofrida).

---

## 4. Arquitetura

```
vonvakvas.sh  (ENTRY POINT / API)
    └── api/router.sh        → roteia o comando (case <comando>)
        └── api/commands.sh  → valida argumentos e chama o script real
            └── scripts/...  → scripts de ação
```

**Camada compartilhada:** `scripts/lib/common.sh`
- Detecta a raiz do projeto dinamicamente (sobe na árvore até achar `config/` ou `.projectroot`).
- Exporta `PROJECT_ROOT`.
- Funções: `config_path <arquivo>`, `script_path <caminho>`, `load_env <arquivo>`.

---

## 5. Estrutura de arquivos (estado atual, 30/08/2026)

```
archiveguiprep/
├── vonvakvas.sh                 ← Entry point / API
├── .projectroot                 ← Marcador de raiz
├── .gitignore                   ← Pronto (telegram.env, cookies, *.tmp, *.log, api/cache/)
├── lore.txt                     ← Explicações pessoais dos scripts
├── api/
│   ├── router.sh
│   └── commands.sh
├── config/
│   ├── archive.txt              ← Histórico de downloads do yt-dlp (~5300 vídeos)
│   ├── succeeded_archvings.txt
│   ├── cookies_alfa.txt         ← Cookies da conta 1 (permissão 600)
│   ├── cookies_beta.txt         ← Cookies da conta 2 (permissão 600)
│   ├── cookies_gama.txt         ← Cookies da conta 3 (permissão 600)
│   ├── channel_list.txt         ← Canais a arquivar (~35 canais, permite # comentários)
│   ├── telegram.env             ← Credenciais Telegram (permissão 600)
│   └── telegram.env.example
├── errors-exp/
│   └── erros.txt                ← Erros conhecidos + soluções (IP real redigido)
├── for-the-model/               ← Material/contexto para modelos de IA
│   ├── agentrules.md
│   ├── cli-reference.md
│   ├── refatoracao-caminhos-dinamicos.md
│   ├── scripts-analysis-report.md
│   └── contexto-completo.md     ← ESTE ARQUIVO
├── scripts/
│   ├── lib/common.sh
│   ├── mainscripts/nts.sh  ntsp.sh
│   ├── organizers/organizer.sh organizeri.sh organizerm.sh
│   │              desorganizar.sh desorganizarm.sh organizerv2.sh
│   ├── masses/mass_nts.sh mass_organizer.sh
│   ├── checker/check.sh
│   └── iaupload/uploaderf.sh
└── your-directory/              ← Vazio (destino das pastas dos canais)
```

---

## 6. Comandos da CLI (via `./vonvakvas.sh`)

| Comando | Atalho | Script | Função |
|---|---|---|---|
| `archive <@canal> [y/n]` | `a` | `scripts/mainscripts/nts.sh` | Baixa os vídeos de um canal do YouTube. `y` = usa cookies (1 de 3 contas aleatória), `n` = modo fantasma (`--no-mark-watched`). |
| `archive-playlist <@canal ou URL> [y/n]` | `apl` (legados: `archive-pro`, `ap`) | `scripts/mainscripts/ntsp.sh` | Variante alternativa do download para playlists/URLs (ntsp = nts playlist); aceita handle ou URL completa. |
| `organize <pasta>` | `org` | `scripts/organizers/organizer.sh` | Organiza arquivos em `descricao/ info_json/ thumbs/ pfp/ videos/`. |
| `organize-instagram <pasta>` | `orgi` | `scripts/organizers/organizeri.sh` | Igual ao organize, mas **sem** `pfp/`. |
| `organize-music <pasta>` | `orgm` | `scripts/organizers/organizerm.sh` | Move `mp4/mkv/webm/mp3` para `musicas/`. |
| `desorganize <pasta>` | `dorg` | `scripts/organizers/desorganizar.sh` | Reverte o organize (move tudo de volta; remove subpastas vazias). |
| `desorganize-music <pasta>` | `dorgm` | `scripts/organizers/desorganizarm.sh` | Reverte o organize-music (`musicas/` → raiz). |
| `prepare-upload <pasta>` | `prep` | `scripts/organizers/organizerv2.sh` | Cria `ia/`, `ia/Videos` e `itemimage` para upload no IA. Requer pasta organizada. |
| `upload <pasta>` | `up` | `scripts/iaupload/uploaderf.sh` | Upload pro Internet Archive (requer subpasta `ia/` e CLI `ia` instalada). |
| `check` | `c` | `scripts/checker/check.sh` | Verifica status HTTP dos canais da lista; alerta via Telegram se algum cair. |
| `mass-archive` | `ma` | `scripts/masses/mass_nts.sh` | Baixa todos os canais da lista (com intervalo aleatório anti-bloqueio). |
| `mass-organize` | `mo` | `scripts/masses/mass_organizer.sh` | Organiza todas as pastas (suporta `.dirignore`). |
| `help` | `-h` | — | Mostra a ajuda. |

**Fluxos principais:**
- Simples: `./vonvakvas.sh archive <canal> y`
- Completo: `archive → organize → prepare-upload → upload`
- Massa: `mass-archive → mass-organize`
**Marcador de raiz:** `.projectroot` (arquivo vazio na raiz).