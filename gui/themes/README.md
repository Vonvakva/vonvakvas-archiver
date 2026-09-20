# Temas da GUI — documentação

Cada arquivo `.json` nesta pasta é um tema da interface. A GUI lista
todos automaticamente na aba **Temas** (nada precisa ser registrado em
código — soltou um JSON aqui, o tema aparece).

## Formato de um tema

```json
{
  "name": "Nome bonito do tema",
  "description": "Uma linha descrevendo a vibe do tema",
  "bg": "#0d1017",
  "bg_alt": "#11151f",
  "panel": "#161b26",
  "panel_alt": "#1d2432",
  "border": "#262e40",
  "text": "#e8ebf2",
  "muted": "#8a93a8",
  "accent": "#8b5cf6",
  "accent_hover": "#a78bfa",
  "accent_pressed": "#7c3aed",
  "success": "#4ade80",
  "danger": "#f87171",
  "warning": "#fbbf24",
  "console_bg": "#0a0d13",
  "gif": {
    "header": "",
    "sidebar": "",
    "dashboard": ""
  },
  "extras": {
    "header_text": "",
    "header_text_color": "",
    "sidebar_text": ""
  }
}
```

- `name` e `description` são metadados exibidos na aba Temas.
- O **id** do tema é o nome do arquivo sem `.json` (ex: `light.json` → id `light`).
- Você **não precisa definir todas as chaves**: o que faltar herda do tema
  padrão (`DEFAULT_COLORS` em `gui/theme.py`). Um tema que só quer mudar o
  acento pode ter 3 linhas.
- Chaves desconhecidas são ignoradas; JSON inválido faz o tema ser pulado
  (a GUI nunca quebra por causa de um tema ruim).

## Os tokens

| Token | Onde aparece |
|---|---|
| `bg` | Fundo geral da janela |
| `bg_alt` | Sidebar, header, campos de texto, listas |
| `panel` | Cards e painéis |
| `panel_alt` | Botões normais, hover de itens |
| `border` | Bordas de tudo |
| `text` | Texto principal |
| `muted` | Textos secundários/dicas |
| `accent` / `accent_hover` / `accent_pressed` | Cor de destaque (botões principais, seleção, logo) |
| `success` / `danger` / `warning` | Chips de status (OK / erro / aviso) |
| `console_bg` | Fundo do console e do editor de arquivos |

Os fundos translúcidos dos chips **não são definidos no tema**: são
derivados de `success`/`danger`/`warning`/`accent` em tempo de execução
(`_derived_tokens()` no `theme.py`). Então um tema claro automaticamente
ganha chips claros.

## Decorações: GIFs, imagens e textos (opcionais)

As seções `"gif"` e `"extras"` são **totalmente opcionais** — campo
vazio (`""`) ou ausente é simplesmente ignorado. Um tema sem decorações
funciona igualzinho.

### Seção `"gif"` — animações/imagens

| Slot | Onde aparece |
|---|---|
| `gif.header` | No header, à direita das infos do sistema |
| `gif.sidebar` | Na sidebar, abaixo do logo "VONVAKVA'S" |
| `gif.dashboard` | No Dashboard, alinhado à direita |

Cada valor pode vir de **duas fontes**:

1. **Internet** — uma URL direta:
   ```json
   "gif": { "sidebar": "https://media.tenor.com/xyz/za-hando.gif" }
   ```
   Baixada **uma vez só** para `config/gui_cache/` (nome por hash da URL,
   então funciona offline depois da primeira vez e nada vai pro /tmp).
   Funciona com GIF animado, PNG, JPG, WebP e BMP.

2. **Arquivo** — o nome do arquivo, SEM caminho:
   ```json
   "gif": { "sidebar": "za_hando.gif" }
   ```
   Nesse caso o tema **precisa ter uma pasta com o MESMO NOME do json**
   dentro de `gui/themes/`, e o arquivo mora lá:
   ```
   gui/themes/
   ├── terminal.json
   └── terminal/            ← pasta com o mesmo nome do json
       └── za_hando.gif
   ```
   Se o arquivo não existir lá, a decoração simplesmente não aparece
   (nada quebra).

### Seção `"extras"` — textos e cores

| Chave | O que faz |
|---|---|
| `header_text` | Texto custom no header (ex: nome do arquivo, uma frase) |
| `header_text_color` | Cor do `header_text` (hex, ex: `"#22d3ee"`) |
| `sidebar_text` | Texto extra na sidebar, abaixo do logo |

Exemplo:
```json
"extras": {
  "header_text": "arquivo pessoal • nao distribuir",
  "header_text_color": "#fbbf24",
  "sidebar_text": "preservando desde 2024 :3"
}
```

### Comportamento em caso de falha

URL fora do ar, arquivo inexistente ou formato inválido → o widget de
decoração **some em silêncio**. Decoração nunca pode derrubar a GUI
(a GUI abre normalmente mesmo com um tema inteiro quebrado).

## Como criar um tema novo (passo a passo)

1. Copie o `default.json` para um arquivo novo, ex: `meutema.json`
   (o id do tema vai ser `meutema`).
2. Edite os valores que quiser. Dica: comece mudando só `accent`,
   `accent_hover` e `accent_pressed` — muda a personalidade inteira.
3. Ajuste `name` e `description`.
4. Salve. Abra a GUI → aba **Temas** → clique em "Recarregar lista"
   (ou reinicie) → selecione → **Aplicar tema**.
5. O tema escolhido fica salvo em `config/gui_state.env`
   (`GUI_THEME="meutema"`) e sobrevive a reinícios.

## Prioridade de resolução (quem ganha de quem)

1. `DEFAULT_COLORS` (em `gui/theme.py`) — base de tudo
2. `gui/themes/<ativo>.json` — sobrescreve o padrão
3. `config/gui_theme.json` — **override manual**, tem a palavra final
   (útil para testar uma cor sem criar arquivo; pode ser deletado quando
   não quiser mais o override)

## Dicas de contraste

- `text` deve contrastar com `bg` e `panel` (é o texto de tudo).
- `muted` fica em cima de `bg`/`panel` — não fique muito discreto.
- Botões `accent` recebem texto **branco**: escolha um `accent` escuro
  o suficiente (ou claro, no caso de temas claros) para isso.
- O console usa `console_bg` com uma cor de texto fixa (#c9d4e8):
  mantenha o console sempre escuro para os logs continuarem legíveis.
