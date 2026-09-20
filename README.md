# Vonvakva's Archive - Documentação Técnica

Documentação técnica para usuários e contribuidores do projeto.

## Índice

- [Instalação](#instalacao)
- [Configuração](#configuracao)
- [Interface Gráfica (GUI)](#interface-grafica-gui)
- [Linha de Comando (CLI)](#linha-de-comando-cli)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Fluxos de Trabalho](#fluxos-de-trabalho)
- [Referência de Comandos](#referencia-de-comandos)
- [Dependências](#dependencias)
- [Solução de Problemas](#solucao-de-problemas)

---

## Instalação

### Requisitos

| Ferramenta | Obrigatório | Descrição |
|------------|-------------|-----------|
| python3 (>=3.10) | Sim | Runtime da GUI |
| ffmpeg | Sim | Merge de vídeo/áudio |
| node.js | Recomendado | Runtime do yt-dlp |
| curl | Sim | Monitoramento de canais |

### Instalação Rápida

```bash
./installer.sh
```

Isso irá:
1. Copiar o projeto para `~/.local/opt/vonvakvas-archive`
2. Criar um ambiente virtual Python com as dependências
3. Gerar arquivos de configuração iniciais
4. Criar atalho no menu de aplicativos

### Instalação Manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuração

### Arquivos de Configuração

Todos os arquivos de configuração ficam em `config/`:

| Arquivo | Finalidade |
|---------|------------|
| `channel_list.txt` | Lista de canais para arquivamento (um por linha, `#` para comentários) |
| `archive.txt` | Histórico de vídeos baixados (gerenciado pelo yt-dlp) |
| `cookies_1.txt` | Cookies da conta YouTube 1 (formato Netscape) |
| `cookies_2.txt` | Cookies da conta YouTube 2 |
| `cookies_3.txt` | Cookies da conta YouTube 3 |
| `telegram.env` | Credenciais do bot Telegram |
| `settings.env` | Configurações gerais (pasta dos canais) |

### Configuração de Cookies

Os cookies são usados para evitar bloqueios do YouTube. Para configurar:

1. Acesse o YouTube logado em uma conta
2. Exporte os cookies no formato Netscape (extensão "Get cookies.txt" recomendada)
3. Salve em `config/cookies_1.txt` (ou 2/3 para contas adicionais)

O sistema sorteia aleatoriamente entre as contas configuradas para distribuir as requisições.

### Configuração do Telegram (Opcional)

```bash
cp config/telegram.env.example config/telegram.env
```

Edite o arquivo com suas credenciais:
```env
TELEGRAM_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id
```

### Pasta dos Canais (HDD Externo)

Para usar uma pasta diferente da padrão (`your-directory/`):

```bash
# Edite config/settings.env
CHANNELS_ROOT="/caminho/para/sua/pasta"
```

---

## Interface Gráfica (GUI)

### Iniciando

```bash
./start-gui.sh
```

### Páginas

#### Dashboard

Visão geral do arquivo com:
- Número de canais na lista
- Total de vídeos arquivados
- Canais salvos antes de caírem
- Pastas de canais existentes
- Status das ferramentas (yt-dlp, ffmpeg, etc.)
- Ações rápidas (verificar canais, arquivar em massa)

#### Arquivar

Baixar do YouTube:
- **Canal**: handle do YouTube (com ou sem @) — usa o comando `archive`
- **Playlist**: URL completa da playlist — usa o comando `archive-playlist`
- **Modo**: com cookies (rotatividade entre 3 contas) ou sem cookies (não marca como assistido)
- **Botões**: "Baixar canal (archive)" ou "Baixar playlist (archive-playlist)"

#### Organizar

Organizar arquivos baixados em subpastas:
- **Ações disponíveis**:
  - Organizar (organize) — separa em descricao/, info_json/, thumbs/, pfp/, videos/
  - Instagram (organize-instagram) — sem pasta pfp/
  - Músicas (organize-music) — move para musicas/
  - Desorganizar (desorganize) — reverte a organização
  - Reverter músicas (desorganize-music) — reverte musicas/
  - Preparar upload IA (prep) — cria estrutura ia/ para upload

#### Upload IA

Enviar para o Internet Archive:
- Valida se a pasta `ia/` existe
- Solicita URL do canal para metadados
- Identifier automático: `<pasta>-<data>`
- Metadados: channel, creator, title, collection, mediatype

#### Monitor

Verificar status dos canais:
- Lista todos os canais da `channel_list.txt`
- Testa HTTP 200 de cada canal
- Envia alerta no Telegram se algum estiver offline

#### Em Massa

Processar toda a lista de canais:
- **Mass archive**: baixa todos os canais com sleep aleatório anti-bloqueio
- **Mass organize**: organiza todas as pastas (respeita `.dirignore`)

#### Editor

Editar arquivos de configuração diretamente pela GUI:
- **Cookies (1, 2 e 3)**: editar cookies no formato Netscape
- **Lista de canais**: editar `channel_list.txt`
- **Telegram**: editar `telegram.env` (token e chat_id)

O editor usa o mesmo estilo do console (fundo escuro, fonte monoespaçada) e permite salvar com um clique.

#### Ajustes

Configurações do sistema:
- Pasta dos canais (pode ser HDD externo)
- Visualização de qual config está sendo usada (projeto vs pasta configurada)
- Copiar configs do projeto para pasta externa

### Console

O console na parte inferior mostra:
- Saída em tempo real dos comandos
- Status de execução
- Botões: Limpar, Parar, Ocultar/Mostrar

---

## Linha de Comando (CLI)

### Sintaxe

```bash
./vonvakvas.sh <comando> [opções]
```

### Exemplos

```bash
# Baixar um canal
./vonvakvas.sh archive lofigirl y

# Organizar pasta
./vonvakvas.sh organize ./pasta-do-canal

# Verificar canais
./vonvakvas.sh check

# Arquivar toda a lista
./vonvakvas.sh mass-archive
```

---

## Estrutura de Pastas

Após a organização, cada canal fica com a seguinte estrutura:

```text
nome-do-canal/
├── descricao/          # Arquivos .description
├── info_json/          # Arquivos .info.json
├── pfp/                # Imagens de perfil (.jpg/.png)
├── thumbs/             # Thumbnails (.webp)
├── videos/             # Vídeos (.mp4/.mkv/.webm)
└── ia/                 # (após prepare-upload)
    ├── itemimage.jpg   # Capa do item
    └── Videos/         # Cópia dos vídeos + metadados
```

---

## Fluxos de Trabalho

### 1. Download Simples

```bash
./vonvakvas.sh archive <canal> y
```

### 2. Download + Organização + Upload

```bash
./vonvakvas.sh archive <canal> y
./vonvakvas.sh organize ./pasta-do-canal
./vonvakvas.sh prepare-upload ./pasta-do-canal
./vonvakvas.sh upload ./pasta-do-canal
```

### 3. Atualização em Massa

```bash
./vonvakvas.sh mass-archive
./vonvakvas.sh mass-organize
```

### 4. Monitoramento

```bash
./vonvakvas.sh check
```

---

## Referência de Comandos

### archive (a)

Baixa vídeos de um canal do YouTube.

```bash
./vonvakvas.sh archive <@canal> [y/n]
```

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `@canal` | Sim | Handle do YouTube |
| `y / n` | Não (padrão: n) | y = usar cookies, n = modo fantasma |

**Flags do yt-dlp:** até 720p, mp4, thumbnails, descrições, info.json, metadados embarcados.

### archive-playlist (apl)

Baixa uma playlist do YouTube. Aceita URL de playlist ou @handle do canal (ntsp = nts playlist).

```bash
./vonvakvas.sh archive-playlist <url-playlist> [y/n]
```

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `url-playlist` | Sim | URL completa da playlist |
| `y / n` | Não (padrão: n) | y = usar cookies, n = modo fantasma |

### organize (org)

Organiza arquivos em subpastas por tipo.

```bash
./vonvakvas.sh organize <pasta>
```

**Estrutura criada:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`

### organize-instagram (orgi)

Organiza arquivos do Instagram (sem pasta `pfp/`).

```bash
./vonvakvas.sh organize-instagram <pasta>
```

### organize-music (orgm)

Organiza arquivos de música.

```bash
./vonvakvas.sh organize-music <pasta>
```

**Estrutura criada:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `musicas/`

### desorganize (dorg)

Reverte a organização (move tudo de volta para a raiz).

```bash
./vonvakvas.sh desorganize <pasta>
```

### desorganize-music (dorgm)

Reverte a organização de músicas.

```bash
./vonvakvas.sh desorganize-music <pasta>
```

### prepare-upload (prep)

Prepara a pasta organizada para upload no Internet Archive.

```bash
./vonvakvas.sh prepare-upload <pasta>
```

**Requer:** pasta organizada com `videos/`, `descricao/`, `info_json/`  
**Cria:** `ia/`, `ia/Videos/`, `ia/<canal>_itemimage.jpg`

### upload (up)

Faz upload para o Internet Archive.

```bash
./vonvakvas.sh upload <pasta>
```

**Requer:** pasta `ia/` (criada pelo prepare-upload), CLI `ia` instalada e configurada.

**Metadados automáticos:**
- `channel`: URL do canal
- `creator`: nome do canal
- `title`: "<canal> archive"
- `collection`: opensource_movies
- `mediatype`: movies
- `subject`: youtube;youtuber;youtube-preservation;youtube-videos;asmr

### check (c)

Verifica status HTTP dos canais da lista.

```bash
./vonvakvas.sh check
```

Envia alerta no Telegram se algum canal retornar código diferente de 200.

### mass-archive (ma)

Baixa todos os canais da `channel_list.txt`.

```bash
./vonvakvas.sh mass-archive
```

**Características:**
- Sleep aleatório entre downloads (2-10 segundos)
- Usa mesma regra de cookies para todo o lote
- Ignora comentários e linhas em branco na lista

### mass-organize (mo)

Organiza todas as pastas do diretório atual.

```bash
./vonvakvas.sh mass-organize
```

**Respeita:** arquivo `.dirignore` (pastas listadas são ignoradas).

---

## Dependências

### Python (requirements.txt)

| Pacote | Versão | Finalidade |
|--------|--------|------------|
| PySide6 | >=6.6 | Interface gráfica Qt |
| psutil | >=5.9 | Gerenciamento de processos |
| yt-dlp | latest | Download de vídeos |
| internetarchive | latest | Upload para IA |

### Sistema

| Ferramenta | Finalidade |
|------------|------------|
| ffmpeg | Merge vídeo/áudio |
| node.js | Runtime JavaScript (yt-dlp) |
| curl | Requisições HTTP |

---

## Solução de Problemas

### Erro: "This video is available to this channel's members"

**Causa:** Vídeo exclusivo para membros do canal.  
**Solução:** Torne-se membro ou ignore (o vídeo não será baixado).

### Erro: Muitas linhas "googlevideo.com"

**Causa:** O canal está fazendo LIVE no momento do download.  
**Solução:**
1. Espere a live terminar e rode novamente
2. Ou comente o canal no `channel_list.txt` temporariamente

### Erro: "Permission denied"

```bash
chmod +x vonvakvas.sh start-gui.sh
```

### Erro: "command not found: yt-dlp"

```bash
pip install yt-dlp
# ou
pip install -r requirements.txt
```

### Upload falha

1. Verifique se a pasta `ia/` existe (rode `prepare-upload` primeiro)
2. Verifique se a CLI `ia` está instalada: `ia --version`
3. Configure suas credenciais: `ia configure`

### GUI não inicia

1. Verifique se o ambiente virtual está ativado
2. Verifique se o PySide6 está instalado: `pip list | grep PySide6`
3. Tente iniciar com debug: `python gui/main.py`