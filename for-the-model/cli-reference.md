# Vonvakva's Archive CLI - Referencia

**Data:** 29/08/2026  
**Versao:** 1.0

---

## O que e?

O CLI (Command Line Interface) unificado permite acessar todas as funcionalidades do projeto atraves de um unico comando: `./vonvakvas.sh`

---

## Inicio Rapido

```bash
# Navegue ate a raiz do projeto
cd /home/flucio/vonvakvasarchiver/archiveguiprep

# Execute um comando
./vonvakvas.sh archive lofigirl y
```

---

## Comandos Disponiveis

### `archive` (atalho: `a`)

Baixa videos de um canal do YouTube.

```bash
./vonvakvas.sh archive <@canal> [y/n]
```

| Argumento | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `@canal` | Sim | Handle do YouTube (com ou sem @) |
| `y/n` | Nao (padrao: n) | Usar cookies (y) ou modo fantasma (n) |

**Exemplos:**
```bash
# Com cookies (recomendado para evitar bloqueios)
./vonvakvas.sh archive lofigirl y

# Sem cookies (modo fantasma)
./vonvakvas.sh archive lofigirl n

# O @ e opcional
./vonvakvas.sh archive LofiGirl y
```

### `archive-playlist` (atalho: `apl`; alias legados: `archive-pro`, `ap`)

Variante alternativa do archive para playlists/URLs (ntsp = nts playlist), chamando o `ntsp.sh`.

```bash
./vonvakvas.sh archive-playlist <@canal|URL> [y/n]
```

| Argumento | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `@canal\|URL` | Sim | Handle do YouTube ou URL completa do canal |
| `y/n` | Nao (padrao: n) | Usar cookies (y) ou modo fantasma (n) |

**Exemplos:**
```bash
# A partir do handle
./vonvakvas.sh archive-playlist lofigirl y

# A partir da URL completa
./vonvakvas.sh archive-playlist https://www.youtube.com/@lofigirl y
```

---
### `organize` (atalho: `org`)

Organiza arquivos de uma pasta em subpastas por tipo.

```bash
./vonvakvas.sh organize <pasta>
```

| Argumento | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `pasta` | Nao (padrao: .) | Caminho para a pasta a organizar |

**Estrutura criada:**
```
pasta/
├── descricao/      # Arquivos .description
├── info_json/      # Arquivos .info.json
├── pfp/            # Imagens .jpg (profile pictures)
├── thumbs/         # Thumbnails .webp
└── videos/         # Videos .mp4/.mkv/.webm
```

**Exemplos:**
```bash
# Organizar pasta especifica
./vonvakvas.sh organize ./your-directory/FlucioVR

# Organizar pasta atual
./vonvakvas.sh organize
```

---

### `organize-instagram` (atalho: `orgi`)

Organiza arquivos baixados do Instagram (chama o `organizeri.sh`). Igual ao organize, mas **sem criar/mover a pasta `pfp/`**.

```bash
./vonvakvas.sh organize-instagram <pasta>
```

### `organize-music` (atalho: `orgm`)

Organiza arquivos de musica (chama o `organizerm.sh`). Move `mp4/mkv/webm/mp3` para uma pasta `musicas/`.

```bash
./vonvakvas.sh organize-music <pasta>
```

### `desorganize` (atalho: `dorg`)

Reverte a organizacao feita pelo `organize` (chama o `desorganizar.sh`): move tudo de volta para a raiz e remove as subpastas vazias (`descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`).

```bash
./vonvakvas.sh desorganize <pasta>
```

**Nota:** Nao reverte a pasta `musicas/` criada pelo `organize-music`.

### `desorganize-music` (atalho: `dorgm`)

Reverte a organizacao de musicas criada pelo `organize-music` (chama o `desorganizarm.sh`): move os arquivos de `musicas/` de volta para a raiz e remove as subpastas vazias.

```bash
./vonvakvas.sh desorganize-music <pasta>
```

### `prepare-upload` (atalho: `prep`)

Prepara uma pasta ja organizada para upload no Internet Archive (chama o `organizerv2.sh`). Cria a pasta `ia/` com os videos e copia a imagem do perfil como `itemimage` do item.

```bash
./vonvakvas.sh prepare-upload <pasta>
```

| Argumento | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `pasta` | Nao (padrao: .) | Pasta organizada (com `videos/`, `descricao/`, `info_json/`) |

**Pre-requisitos:**
- A pasta deve ter sido organizada primeiro: `./vonvakvas.sh organize <pasta>`

**Exemplo:**
```bash
./vonvakvas.sh organize ./your-directory/FlucioVR
./vonvakvas.sh prepare-upload ./your-directory/FlucioVR
./vonvakvas.sh upload ./your-directory/FlucioVR   # depois, o upload
```

---

### `upload` (atalho: `up`)

Faz upload de uma pasta para o Internet Archive.

```bash
./vonvakvas.sh upload <pasta>
```

| Argumento | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `pasta` | Nao (padrao: .) | Caminho para a pasta com subpasta `ia/` |

**Pre-requisitos:**
- A pasta deve conter uma subpasta `ia/` (criada pelo organize + prepare-upload)
- O programa `ia` (internet archive CLI) deve estar instalado

**Exemplo (fluxo completo):**
```bash
./vonvakvas.sh organize ./your-directory/FlucioVR
./vonvakvas.sh prepare-upload ./your-directory/FlucioVR
./vonvakvas.sh upload ./your-directory/FlucioVR
```

---

### `check` (atalho: `c`)

Verifica o status de todos os canais da lista.

---

## Fluxos de Trabalho

### 1. Download Simples

```bash
./vonvakvas.sh archive lofigirl y
```

### 2. Download + Organizar

```bash
./vonvakvas.sh archive lofigirl y
./vonvakvas.sh organize "pasta-do-canal"
```

### 3. Download + Organizar + Preparar + Upload (Completo)

```bash
./vonvakvas.sh archive lofigirl y
./vonvakvas.sh organize "pasta-do-canal"
./vonvakvas.sh prepare-upload "pasta-do-canal"
./vonvakvas.sh upload "pasta-do-canal"
```

### 4. Verificar Canais Offline

```bash
./vonvakvas.sh check
```

### 5. Atualizar Toda a Lista

```bash
./vonvakvas.sh mass-archive
./vonvakvas.sh mass-organize
```

---

## Estrutura de Arquivos do CLI

```
archiveguiprep/
├── vonvakvas.sh          ← Entry point (ponto de entrada)
├── api/
│   ├── router.sh         ← Logica de roteamento
│   └── commands.sh       ← Definicao dos comandos
├── scripts/
│   ├── lib/
│   │   └── common.sh     ← Funcoes compartilhadas
│   ├── mainscripts/
│   │   └── nts.sh        ← Download de videos
│   ├── organizers/
│   │   └── organizer.sh  ← Organizacao de arquivos
│   ├── masses/
│   │   ├── mass_nts.sh
│   │   └── mass_organizer.sh
│   ├── iaupload/
│   │   └── uploaderf.sh  ← Upload para IA
│   └── checker/
│       └── check.sh      ← Verificacao de canais
├── config/
└── your-directory/
```

---

## Como Funciona

```
┌─────────────────────────────────────────────────────────────┐
│ ./vonvakvas.sh archive lofigirl y                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ api/router.sh                                               │
│   - Recebe o comando "archive"                              │
│   - Rota para cmd_archive()                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ api/commands.sh                                             │
│   - cmd_archive("lofigirl", "y")                            │
│   - Valida argumentos                                       │
│   - Chama o script real                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ scripts/mainscripts/nts.sh lofigirl y                       │
│   - Executa o download                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Dicas

1. **Use cookies (`y`) para canais grandes** - Evita bloqueios do YouTube
2. **Organize antes de fazer upload** - O upload requer a pasta `ia/`
3. **Execute `check` periodicamente** - Monitora canais offline
4. **Use atalhos** - `a` para archive, `c` para check, etc.

---

## Solucao de Problemas

### Erro: "Permission denied"
```bash
chmod +x vonvakvas.sh
```

### Erro: "command not found"
Certifique-se de estar na raiz do projeto:
```bash
cd /home/flucio/vonvakvasarchiver/archiveguiprep
```

### Erro ao fazer upload
Verifica se a pasta `ia/` existe:
```bash
./vonvakvas.sh organize <pasta>  # Primeiro organize
./vonvakvas.sh upload <pasta>    # Depois faca upload
```

---

## Configuracao do Sistema (Opcional)

Para usar o comando de qualquer lugar:

```bash
# Crie um alias no ~/.bashrc ou ~/.zshrc
echo 'alias vonvakvas="/home/flucio/vonvakvasarchiver/archiveguiprep/vonvakvas.sh"' >> ~/.bashrc
source ~/.bashrc

# Agora use de qualquer diretorio:
vonvakvas archive lofigirl y
vonvakvas check
```

Ou crie um symlink:
```bash
sudo ln -s /home/flucio/vonvakvasarchiver/archiveguiprep/vonvakvas.sh /usr/local/bin/vonvakvas
```
```bash
./vonvakvas.sh check
```

**O que faz:**
- Verifica se os canais estao online (HTTP 200)
- Envia alerta no Telegram se algum canal estiver offline
- Usa a lista de `config/channel_list.txt`

**Exemplo:**
```bash
./vonvakvas.sh check
```

---

### `mass-archive` (atalho: `ma`)

Baixa todos os canais da lista em massa.

```bash
./vonvakvas.sh mass-archive
```

**O que faz:**
- Le a lista de `config/channel_list.txt`
- Baixa todos os canais um por um
- Usa sleep randomico entre downloads para evitar bloqueios

**Exemplo:**
```bash
./vonvakvas.sh mass-archive
```

---

### `mass-organize` (atalho: `mo`)

Organiza todas as pastas de canais.

```bash
./vonvakvas.sh mass-organize
```

**O que faz:**
- Percorre todas as pastas do diretorio atual
- Ignora pastas listadas em `.dirignore`
- Executa o organizer em cada pasta

**Exemplo:**
```bash
./vonvakvas.sh mass-organize
```

---

### `help` (atalho: `-h`, `--help`)

Mostra a mensagem de ajuda com todos os comandos.

```bash
./vonvakvas.sh help
./vonvakvas.sh --help
./vonvakvas.sh -h
```