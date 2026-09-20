# Extensões da GUI — documentação

Extensões são widgets custom feitos em Python: um `.py` nesta pasta
coleta uma informação (do sistema, de um arquivo, de onde quiser) e a
GUI mostra no **header** (chip compacto) e/ou no **dashboard** (cartão
grande), atualizando de tempos em tempos.

> ⚠️ **Segurança:** extensão é código rodando na sua máquina, com seu
> usuário — mesmo nível de confiança dos scripts Bash em `scripts/`.
> Só coloque aqui `.py` que você escreveu ou confia.

## Contrato de uma extensão

```python
# gui/extensions/meu_widget.py

NAME = "Nome exibido"             # obrigatório (str)

WHERE = ["header", "dashboard"]   # obrigatório: "header", "dashboard"
                                  # ou os dois

REFRESH = 5                       # opcional: segundos entre leituras
                                  # (padrão 5, mínimo 1, máximo 3600)

def get_value():
    # obrigatório: retorna (texto, estado)
    return ("42°C", "warn")
```

### `get_value()`

- Retorna `(texto, estado)` — ou só o texto (o estado vira `"ok"`).
- **Estados** (coloridos com o tema ativo):
  - `"ok"` — verde (chip verde no header / normal no dashboard)
  - `"warn"` — amarelo
  - `"bad"` — vermelho
  - `"muted"` — neutro
- **Deve ser rápido** (~<100ms): roda na thread da interface. Ler
  arquivo, chamar psutil, subprocess com timeout curto — ok. Baixar
  coisa da internet dentro do `get_value` — não (use cache e atualize
  por fora).

## Regras da pasta

| Regra | Efeito |
|---|---|
| Só `*.py` é lido | Outros arquivos são ignorados |
| Nome começando com `_` | **Não carrega** (use para templates — veja `_exemplo.py`) |
| Erro de sintaxe/import | Extensão pulada + aviso na aba Extensões |
| `get_value()` dando erro | Widget mostra "erro" (vermelho); a GUI segue de pé |
| Falta `NAME`/`WHERE`/`get_value` | Extensão pulada + aviso |

`id` da extensão = nome do arquivo sem `.py` (é o que aparece no
`EXT_DISABLED` do `config/gui_state.env`).

## Gerenciando pela GUI

Aba **Extensões**:
- Lista tudo que carregou, com o último valor de cada uma
- **Ativar/Desativar** — persiste em `config/gui_state.env`
  (`EXT_DISABLED="id1,id2"`); desativada sai do header/dashboard mas
  continua na lista
- **Recarregar** — re-escaneia a pasta (depois de criar/editar um `.py`)
- **Abrir pasta** — abre no gerenciador de arquivos

No terminal: `VONVAKVAS_*` não interfere; desativar manualmente é só
editar o `EXT_DISABLED` (ou tirar o arquivo da pasta).

## Exemplo passo a passo (temperatura fictícia da GPU)

1. `gui/extensions/gpu_temp.py`:
   ```python
   NAME = "GPU"
   WHERE = ["header"]
   REFRESH = 10

   def get_value():
       with open("/sys/class/drm/card0/temp1_input") as f:
           milli = int(f.read().strip())
       c = milli // 1000
       if c > 85:
           return (f"{c}°C", "bad")
       if c > 70:
           return (f"{c}°C", "warn")
       return (f"{c}°C", "ok")
   ```
2. Aba Extensões → **Recarregar** → aparece na lista → ativa por padrão.
3. O chip "GPU: 62°C" aparece no header, verde/amarelo/vermelho conforme
   a temperatura, usando as cores do tema ativo.

Dica: o `_exemplo.py` da pasta é um modelo pronto e funcional (mostra
há quanto tempo a GUI está aberta) — copie, renomeie e edite.

## Interações (Botões)

Para adicionar botões clicáveis:

```python
INTERACTIONS = [
    {"id": "play", "label": "▶", "tooltip": "Tocar"},
    {"id": "pause", "label": "⏸", "tooltip": "Pausar"},
]

def on_interaction(interaction_id: str, ext):
    if interaction_id == "play":
        return ("Tocando...", "ok")
    return None
```

## Estados Válidos

- `"ok"` - Verde (tudo certo)
- `"warn"` - Amarelo (atenção)
- `"bad"` - Vermelho (erro)
- `"muted"` - Cinza (neutro/inativo)

## Sandbox

- Timeout de 5 segundos para `get_value()` e `on_interaction()`
- Execução em thread separada (não trava a GUI)
- Extensões com erro NUNCA derrubam a GUI

## Regras

- Arquivos começando com `_` são ignorados (templates)
- `get_value()` deve ser rápido (<100ms)
- Use subprocess para operações longas
- Extensões são recarregadas ao clicar "Recarregar" na GUI

## Exemplo Completo: Player de Música

```python
import subprocess

NAME = "🎵 Player"
WHERE = ["dashboard"]
REFRESH = 2

INTERACTIONS = [
    {"id": "prev", "label": "⏮", "tooltip": "Anterior"},
    {"id": "play", "label": "▶", "tooltip": "Tocar"},
    {"id": "pause", "label": "⏸", "tooltip": "Pausar"},
    {"id": "next", "label": "⏭", "tooltip": "Próxima"},
]

_is_playing = False

def get_value():
    if _is_playing:
        return ("Tocando", "ok")
    return ("Parado", "muted")

def on_interaction(interaction_id, ext):
    global _is_playing
    if interaction_id == "play":
        subprocess.Popen(["mpc", "play"])
        _is_playing = True
        return ("Tocando", "ok")
    elif interaction_id == "pause":
        subprocess.Popen(["mpc", "pause"])
        _is_playing = False
        return ("Pausado", "warn")
    return None

## Nerd Fonts e Ícones

A GUI suporta **Nerd Fonts**! Você pode usar ícones Unicode nos labels dos botões e no texto das extensões.

### Configurando uma Nerd Font

No arquivo de tema JSON (`gui/themes/<id>.json`), adicione a seção `font`:

```json
{
    "name": "Meu Tema",
    "font": {
        "family": "JetBrainsMono Nerd Font",
        "size": 13
    },
    "colors": {
        "bg": "#0d1017",
        "accent": "#8b5cf6"
    }
}
```

### Nerd Fonts Populares

- `JetBrainsMono Nerd Font`
- `FiraCode Nerd Font`
- `Hack Nerd Font`
- `SourceCodePro Nerd Font` (CodeNewRoman)
- `UbuntuMono Nerd Font`

### Exemplo com Ícones Nerd Font

```python
NAME = "🎵 Player"
WHERE = ["dashboard"]

INTERACTIONS = [
    {"id": "prev", "label": "󰒮", "tooltip": "Anterior"},
    {"id": "play", "label": "󰐊", "tooltip": "Tocar"},
    {"id": "pause", "label": "󰏤", "tooltip": "Pausar"},
    {"id": "next", "label": "󰒭", "tooltip": "Próxima"},
]
```

### Compatibilidade

- ✅ Unicode padrão (▶, ⏸, ⏮, ⏭) - funciona em qualquer fonte
- ✅ Emojis (🎵, 🔥, 💾) - funciona se a fonte suportar emoji
- ✅ Ícones Nerd Font (󰒮, 󰐊) - funciona se a Nerd Font estiver configurada no tema
- ⚠️ Se a fonte não tiver o glifo, aparece um quadrado vazio ou ponto de interrogação
```	
