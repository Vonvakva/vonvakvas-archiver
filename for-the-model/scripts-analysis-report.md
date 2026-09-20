# Relatorio de Analise de Scripts - Vonvakva's Archive

**Data:** 29/08/2026  
**Objetivo:** Documentar caminhos, dependencias e propor solucao para execucao independente de localizacao.

---

## 1. Inventario de Scripts

| Script | Localizacao | Funcao |
|--------|-------------|--------|
| `nts.sh` | `scripts/mainscripts/` | Download de canal do YouTube via yt-dlp |
| `ntsp.sh` | `scripts/mainscripts/` | Versao "publica" do nts.sh (sem cookies) |
| `organizer.sh` | `scripts/organizers/` | Organiza arquivos em subpastas |
| `organizeri.sh` | `scripts/organizers/` | Variante do organizer (sem pfp) |
| `organizerm.sh` | `scripts/organizers/` | Variante para musicas |
| `desorganizar.sh` | `scripts/organizers/` | Reverte organizacao |
| `mass_nts.sh` | `scripts/masses/` | Executa nts.sh para toda a lista |
| `mass_organizer.sh` | `scripts/masses/` | Executa organizer.sh em massa |
| `uploaderf.sh` | `scripts/iaupload/` | Upload para Internet Archive |
| `check.sh` | `scripts/checker/` | Verifica status dos canais |

---

## 2. Mapeamento de Caminhos Relativos

### 2.1 Scripts que referenciam `../config/`

| Script | Referencia | Contexto |
|--------|------------|----------|
| `nts.sh` | `../config/archive.txt` | Historico de downloads |
| `nts.sh` | `../config/cookies_alfa.txt` | Cookies conta 1 |
| `nts.sh` | `../config/cookies_beta.txt` | Cookies conta 2 |
| `nts.sh` | `../config/cookies_gama.txt` | Cookies conta 3 |
| `ntsp.sh` | `../config/archive.txt` | Historico de downloads |
| `ntsp.sh` | `../config/cookies_alfa.txt` | Cookies conta 1 |
| `ntsp.sh` | `../config/cookies_beta.txt` | Cookies conta 2 |
| `ntsp.sh` | `../config/cookies_gama.txt` | Cookies conta 3 |
| `mass_nts.sh` | `../config/channel_list.txt` | Lista de canais |
| `check.sh` | `../config/channel_list.txt` | Lista de canais |

### 2.2 Scripts que referenciam outros scripts

| Script | Referencia | Contexto |
|--------|------------|----------|
| `mass_nts.sh` | `../scripts/mainscripts/nts.sh` | Chama script de download |
| `mass_organizer.sh` | `../scripts/organizers/organizer.sh` | Chama script organizador |

---

## 3. Problemas Identificados

### 3.1 Dependencia de Working Directory
Todos os scripts assumem que serao executados de diretorios especificos:
- `nts.sh` e `ntsp.sh` devem rodar de dentro de `scripts/mainscripts/`
- `mass_nts.sh` deve rodar de dentro de `scripts/masses/`
- `mass_organizer.sh` deve rodar de dentro de `scripts/masses/`
- `check.sh` deve rodar de dentro de `scripts/checker/`

### 3.2 Caminhos quebrados em `mass_nts.sh`
```bash
# Linha 31 - Caminho incorreto:
../scripts/mainscripts/nts.sh "$canal" "$RESPOSTA"
# O correto seria:
../mainscripts/nts.sh "$canal" "$RESPOSTA"
```
O script esta em `scripts/masses/` e referencia `../scripts/mainscripts/` que nao existe.

### 3.3 Variaveis hardcoded
- `check.sh` possui token do Telegram e chat_id hardcoded

---

## 4. Proposta de Refatoracao

### 4.1 Estrutura de Diretorios Sugerida

```
archiveguiprep/
├── config/                    # Configuracoes (permanece)
├── scripts/
│   ├── lib/
│   │   └── common.sh          # Funcoes compartilhadas
│   ├── mainscripts/
│   ├── organizers/
│   ├── masses/
│   ├── iaupload/
│   └── checker/
└── your-directory/
```

### 4.2 Abordagem: Script `lib/common.sh`

Criar um arquivo comum que calcule o root do projeto:

```bash
#!/bin/bash
# scripts/lib/common.sh

detect_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    while [[ "$script_dir" != "/" ]]; do
        if [[ -d "$script_dir/config" ]] || [[ -f "$script_dir/.projectroot" ]]; then
            echo "$script_dir"
            return 0
        fi
        script_dir="$(dirname "$script_dir")"
    done
    echo "Erro: Nao foi possivel encontrar a raiz do projeto" >&2
    return 1
}

export PROJECT_ROOT="$(detect_project_root)"

config_path() {
    echo "$PROJECT_ROOT/config/$1"
}

script_path() {
    echo "$PROJECT_ROOT/scripts/$1"
}
```

### 4.3 Como usar nos scripts

```bash
#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Agora pode usar:
# --download-archive "$(config_path archive.txt)"
# --cookies "$(config_path cookies_alfa.txt)"
```

### 4.4 Alternativa: Marcador de Projeto

Criar arquivo `.projectroot` na raiz do projeto para facilitar deteccao.

---

## 5. Plano de Migracao (Incremental)

### Fase 1: Criar infraestrutura
1. Criar `scripts/lib/common.sh` com funcoes de deteccao de paths
2. Criar marcador `.projectroot` na raiz do projeto

### Fase 2: Corrigir bugs existentes
1. Corrigir caminho em `mass_nts.sh` (linha 31)

### Fase 3: Migrar scripts um a um
1. Comecar pelos scripts mais simples (`organizer.sh`, `desorganizar.sh`)
2. Migrar `nts.sh` e `ntsp.sh`
3. Migrar scripts em massa
4. Migrar `uploaderf.sh`

### Fase 4: Testar
1. Executar cada script de diferentes diretorios
2. Verificar se caminhos estao sendo resolvidos corretamente

---

## 6. Observacoes de Seguranca

1. **Credenciais hardcoded**: `check.sh` expoe token do Telegram
   - **Sugestao**: Mover para `config/telegram.env` e carregar via `source`

2. **Cookies**: Arquivos de cookies em texto plano
   - **Sugestao**: Adicionar ao `.gitignore` se nao estiver

---

## 7. Beneficios da Refatoracao

| Antes | Depois |
|-------|--------|
| Scripts so funcionam de diretorios especificos | Scripts funcionam de qualquer lugar |
| Caminhos relativos ageis | Caminhos calculados dinamicamente |
| Dificil de criar wrappers/atalhos | Facil criar scripts de conveniencia |
| Bug em `mass_nts.sh` sem correcao | Todos os caminhos verificados |

---

## 8. Notas para o Desenvolvedor

1. **Preservar comportamento**: A refatoracao nao deve alterar o comportamento dos scripts, apenas como eles localizam recursos.

2. **Manter compatibilidade**: Scripts devem continuar funcionando da forma atual durante a transicao.

3. **Testar incrementalmente**: Apos cada mudanca, testar o script afetado.

4. **Documentar**: Atualizar este relatorio conforme mudancas sao feitas.