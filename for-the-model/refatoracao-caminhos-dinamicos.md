# Refatoracao: Caminhos Dinamicos

**Data:** 29/08/2026  
**Objetivo:** Tornar todos os scripts independentes do diretorio de execucao

---

## Resumo

Todos os scripts do projeto foram atualizados para usar um sistema de caminhos dinamicos. Agora eles podem ser executados de qualquer diretorio, sem depender de caminhos relativos fixos.

---

## Arquivos Criados

### 1. `scripts/lib/common.sh`

Arquivo central com funcoes compartilhadas por todos os scripts.

**Funcoes disponiveis:**

| Funcao | Descricao | Exemplo |
|--------|-----------|---------|
| `detect_project_root()` | Detecta a raiz do projeto automaticamente | Usado internamente |
| `config_path <arquivo>` | Retorna caminho completo em `config/` | `$(config_path archive.txt)` |
| `script_path <script>` | Retorna caminho completo em `scripts/` | `$(script_path mainscripts/nts.sh)` |
| `load_env <arquivo>` | Carrega variaveis de um arquivo `.env` | `load_env config/telegram.env` |

**Variavel exportada:**
- `PROJECT_ROOT` - Caminho absoluto para a raiz do projeto

**Como funciona:**
1. Usa `BASH_SOURCE[0]` para encontrar o diretorio do script atual
2. Sobe na arvore de diretorios ate encontrar `.projectroot` ou pasta `config/`
3. Exporta `PROJECT_ROOT` com o caminho encontrado

### 2. `config/telegram.env`

Arquivo de configuracao do Telegram (movido do `check.sh` para maior seguranca).

**Conteudo:**
```
TELEGRAM_TOKEN=<SEU_TOKEN_AQUI>   # ATENCAO: valor real removido por seguranca (30/08/2026)
TELEGRAM_CHAT_ID=<SEU_CHAT_ID_AQUI>
```

**Nota:** Considere adicionar este arquivo ao `.gitignore` por conter tokens sensiveis.

---

## Scripts Atualizados

### `scripts/mainscripts/nts.sh`

**Alteracoes:**
- Adicionado `source` do `common.sh` no inicio
- `../config/cookies_alfa.txt` → `$(config_path cookies_alfa.txt)`
- `../config/cookies_beta.txt` → `$(config_path cookies_beta.txt)`
- `../config/cookies_gama.txt` → `$(config_path cookies_gama.txt)`
- `../config/archive.txt` → `$(config_path archive.txt)`

**Antes:**
```bash
EXTRA_FLAGS="--cookies ../config/cookies_alfa.txt"
--download-archive ../config/archive.txt
```

**Depois:**
```bash
EXTRA_FLAGS="--cookies $(config_path cookies_alfa.txt)"
--download-archive "$(config_path archive.txt)"
```

---

### `scripts/mainscripts/ntsp.sh`

**Alteracoes:** Mesmas alteracoes do `nts.sh`

---

### `scripts/masses/mass_nts.sh`

**Alteracoes:**
- Adicionado `source` do `common.sh` no inicio
- `../config/channel_list.txt` → `$(config_path channel_list.txt)`
- `../mainscripts/nts.sh` → `$(script_path mainscripts/nts.sh)`
- Corrigido bug no caminho do script (antes: `../scripts/mainscripts/nts.sh`)
- Adicionado sleep randomico que estava faltando no codigo original

**Antes:**
```bash
LISTA="../config/channel_list.txt"
../mainscripts/nts.sh "$canal" "$RESPOSTA"
```

**Depois:**
```bash
LISTA="$(config_path channel_list.txt)"
bash "$(script_path mainscripts/nts.sh)" "$canal" "$RESPOSTA"
```

---

### `scripts/masses/mass_organizer.sh`

**Alteracoes:**
- Adicionado `source` do `common.sh` no inicio
- `../scripts/organizers/organizer.sh` → `$(script_path organizers/organizer.sh)`

**Antes:**
```bash
ORGANIZER_SCRIPT="../scripts/organizers/organizer.sh"
```
---

## Testes Realizados

### Teste 1: Deteccao da raiz do projeto

```bash
cd /home/flucio/vonvakvasarchiver/archiveguiprep
source scripts/lib/common.sh
echo $PROJECT_ROOT
```

**Resultado:**
```
/home/flucio/vonvakvasarchiver/archiveguiprep
```

### Teste 2: Funcoes de caminho

```bash
config_path archive.txt
script_path mainscripts/nts.sh
```

**Resultado:**
```
/home/flucio/vonvakvasarchiver/archiveguiprep/config/archive.txt
/home/flucio/vonvakvasarchiver/archiveguiprep/scripts/mainscripts/nts.sh
```

### Teste 3: Execucao de script de outro diretorio

```bash
cd /tmp
bash /home/flucio/vonvakvasarchiver/archiveguiprep/scripts/checker/check.sh
```

**Resultado:**
```
==================================================
 AUDITORIA RAPIDA DE CANAIS (PROJETO NTS)
==================================================
 [200 OK]  -> @snapplesasmr
 [200 OK]  -> @boyslovver
 [200 OK]  -> @carolitaASMR
 ...
```

**Status:** Testes aprovados

---

## Estrutura Final do Projeto

```
archiveguiprep/
├── .projectroot                          # Marcador da raiz do projeto
├── config/
│   ├── archive.txt
│   ├── channel_list.txt
│   ├── cookies_alfa.txt
│   ├── cookies_beta.txt
│   ├── cookies_gama.txt
│   └── telegram.env                      # Novo: credenciais do Telegram
├── scripts/
│   ├── lib/
│   │   └── common.sh                     # Novo: funcoes compartilhadas
│   ├── mainscripts/
│   │   ├── nts.sh                        # Atualizado
│   │   └── ntsp.sh                       # Atualizado
│   ├── organizers/
│   │   ├── organizer.sh                  # Atualizado
│   │   ├── organizeri.sh                 # Atualizado
│   │   ├── organizerm.sh                 # Atualizado
│   │   └── desorganizar.sh               # Atualizado
│   ├── masses/
│   │   ├── mass_nts.sh                   # Atualizado
│   │   └── mass_organizer.sh             # Atualizado
│   ├── iaupload/
│   │   └── uploaderf.sh                  # Atualizado
│   └── checker/
│       └── check.sh                      # Atualizado
├── your-directory/
└── for-the-model/
    ├── agentrules.md
    ├── scripts-analysis-report.md
    └── refatoracao-caminhos-dinamicos.md  # Este arquivo
```

---

## Beneficios da Refatoracao

| Antes | Depois |
|-------|--------|
| Scripts so funcionavam de diretorios especificos | Scripts funcionam de qualquer lugar |
| Caminhos relativos frageis (`../config/`) | Caminhos dinamicos (`$(config_path ...)`) |
| Bug no `mass_nts.sh` (caminho incorreto) | Bug corrigido |
| Credenciais expostas no codigo | Credenciais em arquivo `.env` separado |
| Dificil criar wrappers/atalhos | Facil criar scripts de conveniencia |

---

## Recomendacoes de Seguranca

1. **Adicionar ao `.gitignore`:**
   ```
   config/telegram.env
   config/cookies_*.txt
   ```

2. **Remover tokens do controle de versao (se ja commitado):**
   ```bash
   git rm --cached config/telegram.env
   git rm --cached config/cookies_*.txt
   ```

3. **Criar um arquivo de exemplo:**
   ```
   config/telegram.env.example  # Sem valores reais
   ```

---

## Proximos Passos Sugeridos

1. Testar todos os scripts em ambiente de producao
2. Adicionar `.gitignore` para arquivos sensiveis
3. Considerar criptografia para arquivos de cookies
4. Documentar novo padrao para futuros scripts

**Depois:**
```bash
ORGANIZER_SCRIPT="$(script_path organizers/organizer.sh)"
```

---

### `scripts/checker/check.sh`

**Alteracoes:**
- Adicionado `source` do `common.sh` no inicio
- Adicionado `load_env` para carregar credenciais do Telegram
- `../config/channel_list.txt` → `$(config_path channel_list.txt)`
- TOKEN e CHAT_ID movidos para `config/telegram.env`
- Adicionados fallbacks caso o `.env` nao exista

**Antes:**
```bash
TOKEN="<SEU_TOKEN_AQUI>"   # valor real removido por seguranca
CHAT_ID="<SEU_CHAT_ID_AQUI>"
LISTA="../config/channel_list.txt"
```

**Depois:**
```bash
load_env "$(config_path telegram.env)"
TOKEN="${TELEGRAM_TOKEN:-${TOKEN:-}}"
CHAT_ID="${TELEGRAM_CHAT_ID:-${CHAT_ID:-}}"
LISTA="$(config_path channel_list.txt)"
# Hardening (30/08/2026): enviar_telegram() valida TOKEN/CHAT_ID antes de chamar a API.
# Nenhum segredo fica embutido no codigo; o fallback e via variaveis ja exportadas.
```

---

### Scripts Organizadores

Os seguintes scripts foram atualizados com o `source` do `common.sh`:

- `scripts/organizers/organizer.sh`
- `scripts/organizers/organizeri.sh`
- `scripts/organizers/organizerm.sh`
- `scripts/organizers/desorganizar.sh`

**Nota:** Estes scripts usam `$(pwd)` para o diretorio atual, que e o comportamento esperado. O `common.sh` foi adicionado para consistencia e futuras melhorias.

---

### `scripts/iaupload/uploaderf.sh`

**Alteracoes:**
- Adicionado `source` do `common.sh` no inicio

---

## Como Usar o common.sh

### Adicionar um novo script

```bash
#!/bin/bash

# Carrega funcoes comuns do projeto (sempre incluir)
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Agora pode usar as funcoes:
echo "Raiz do projeto: $PROJECT_ROOT"
ARQUIVO_CONFIG="$(config_path meu_config.txt)"
OUTRO_SCRIPT="$(script_path pasta/outro_script.sh)"
```

### A partir de um script em qualquer subdiretorio

O caminho ate o `common.sh` e sempre relativo ao script atual:

```bash
# Se o script esta em scripts/mainscripts/
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Se o script esta em scripts/masses/
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Se o script esta em scripts/organizers/
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"
```

Em todos os casos, o `../lib/common.sh` sobe um nivel e entra na pasta `lib/`.