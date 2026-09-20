"""i18n — GUI internationalization for Vonvakva's Archive.

Allows switching the interface language (Português / Español / English).
All visible texts go through tr("key"): they are resolved in the ACTIVE
language, with fallback to Portuguese (the project base language) if missing.

The chosen language is persisted in config/gui_state.env (GUI_LANG), the same
file where GUI_THEME and GUI_PROFILE live (see theme.py). The GUI reads the
preference when building the interface and re-applies it live when changed in
the Settings page.

Usage:
    import i18n
    i18n.tr("settings.title")             # text in the active language
    i18n.tr("archive.none", canal="x")    # with {canal} formatting
    i18n.set_language("es")               # changes and persists
"""

from __future__ import annotations

from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GUI_DIR.parent
STATE_FILE = PROJECT_ROOT / "config" / "gui_state.env"

# Códigos y nombres nativos de los idiomas soportados.
LANGUAGES: dict[str, str] = {
    "pt": "Português (Brasil)",
    "es": "Español",
    "en": "English",
}

DEFAULT_LANG = "pt"

# Catálogo:  clave -> { "pt": ..., "es": ..., "en": ... }
_T: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------- NAV
    "nav.dash": {"pt": "Dashboard", "es": "Panel", "en": "Dashboard"},
    "sub.dash": {"pt": "Visão geral do arquivo", "es": "Resumen del archivo",
                 "en": "Archive overview"},
    "nav.archive": {"pt": "Arquivar", "es": "Archivar", "en": "Archive"},
    "sub.archive": {"pt": "Baixar canais do YouTube via yt-dlp",
                    "es": "Descargar canales de YouTube via yt-dlp",
                    "en": "Download YouTube channels via yt-dlp"},
    "nav.organize": {"pt": "Organizar", "es": "Organizar", "en": "Organize"},
    "sub.organize": {"pt": "Organizar as pastas baixadas",
                     "es": "Organizar las carpetas descargadas",
                     "en": "Organize downloaded folders"},
    "nav.upload": {"pt": "Upload IA", "es": "Subir a IA",
                   "en": "Internet Archive Upload"},
    "sub.upload": {"pt": "Preservar itens no Internet Archive",
                   "es": "Preservar elementos en Internet Archive",
                   "en": "Preserve items on the Internet Archive"},
    "nav.monitor": {"pt": "Monitor", "es": "Monitor", "en": "Monitor"},
    "sub.monitor": {"pt": "Checar status dos canais da lista",
                    "es": "Comprobar el estado de los canales de la lista",
                    "en": "Check channel status from the list"},
    "nav.mass": {"pt": "Em massa", "es": "En masa", "en": "Bulk"},
    "sub.mass": {"pt": "Processar a lista inteira de canais",
                 "es": "Procesar toda la lista de canales",
                 "en": "Process the whole channel list"},
    "nav.editor": {"pt": "Editor", "es": "Editor", "en": "Editor"},
    "sub.editor": {"pt": "Editar listas, cookies e telegram.env",
                   "es": "Editar listas, cookies y telegram.env",
                   "en": "Edit lists, cookies and telegram.env"},
    "nav.profiles": {"pt": "Perfis", "es": "Perfiles", "en": "Profiles"},
    "sub.profiles": {"pt": "Instâncias isoladas de configuração",
                     "es": "Instancias de configuración aisladas",
                     "en": "Isolated configuration instances"},
    "nav.themes": {"pt": "Temas", "es": "Temas", "en": "Themes"},
    "sub.themes": {"pt": "Personalize as cores da interface",
                   "es": "Personaliza los colores de la interfaz",
                   "en": "Customize the interface colors"},
    "nav.extensions": {"pt": "Extensões", "es": "Extensiones",
                       "en": "Extensions"},
    "sub.extensions": {"pt": "Widgets custom feitos em Python",
                       "es": "Widgets personalizados en Python",
                       "en": "Custom widgets written in Python"},
    "nav.settings": {"pt": "Ajustes", "es": "Ajustes", "en": "Settings"},
    "sub.settings": {"pt": "Idioma, perfil e pasta dos canais",
                     "es": "Idioma, perfil y carpeta de canales",
                     "en": "Language, profile and channel folder"},
    # ------------------------------------------------------------ Estado
    "busy.running": {"pt": "● executando...", "es": "● ejecutando...",
                     "en": "● running..."},
    "console.done": {"pt": "Concluído ✓", "es": "Completado ✓",
                     "en": "Done ✓"},
    "console.failed": {"pt": "Falhou ✗ (código {code})",
                       "es": "Falló ✗ (código {code})",
                       "en": "Failed ✗ (code {code})"},
    "console.finished": {"pt": "[finalizado — código de saída {code}]",
                         "es": "[finalizado — código de salida {code}]",
                         "en": "[finished — exit code {code}]"},
    "console.stopping": {"pt": "\n[parando processo...]\n",
                         "es": "\n[deteniendo proceso...]\n",
                         "en": "\n[stopping process...]\n"},
    "console.parando": {"pt": "Parando...", "es": "Deteniendo...",
                        "en": "Stopping..."},
    "console.default_profile": {"pt": "padrão do projeto",
                                "es": "config. por defecto del proyecto",
                                "en": "default project config"},
    "console.status_running": {"pt": "Executando: {cmd}",
                               "es": "Ejecutando: {cmd}",
                               "en": "Running: {cmd}"},
    "console.profile_active": {"pt": "\n[perfil ativo: {name}]\n",
                               "es": "\n[perfil activo: {name}]\n",
                               "en": "\n[active profile: {name}]\n"},
    "console.running_warn_title": {"pt": "Perfil", "es": "Perfil",
                                   "en": "Profile"},
    "console.running_warn": {"pt": "Existe um comando em execução.\n"
                                   "Troque o perfil quando ele terminar "
                                   "(o console mostra o status).",
                             "es": "Hay un comando en ejecución.\n"
                                   "Cambia de perfil cuando termine "
                                   "(el console muestra el estado).",
                             "en": "A command is currently running.\n"
                                   "Switch profiles when it finishes "
                                   "(check the console for status)."},

    # ------------------------------------------------------- Header
    "header.profile": {"pt": "PERFIL", "es": "PERFIL", "en": "PROFILE"},
    "header.default_profile": {"pt": "padrão do projeto",
                               "es": "config. por defecto del proyecto",
                               "en": "default project config"},
    "header.profile_tooltip": {
        "pt": "Perfis isolam a configuração (lista de canais, cookies,\n"
              "telegram.env, archive.txt e pasta dos canais) — quase\n"
              "como instâncias independentes. Gerencie na página Perfis.",
        "es": "Los perfiles aíslan la configuración (lista de canales,\n"
              "cookies, telegram.env, archive.txt y carpeta de canales) —\n"
              "casi como instancias independientes. Gestiona en Perfiles.",
        "en": "Profiles isolate the config (channel list, cookies,\n"
              "telegram.env, archive.txt and channel folder) — almost\n"
              "like independent instances. Manage them in Profiles."},
    "header.tip_host": {"pt": "Hostname da máquina",
                        "es": "Hostname de la máquina",
                        "en": "Machine hostname"},
    "header.tip_os": {"pt": "Sistema operacional", "es": "Sistema operativo",
                      "en": "Operating system"},
    "header.tip_date": {"pt": "Data e hora", "es": "Fecha y hora",
                        "en": "Date and time"},
    "header.tip_disk": {"pt": "Espaço livre no disco da pasta dos canais",
                        "es": "Espacio libre en el disco de la carpeta de canales",
                        "en": "Free space on the channel folder disk"},
    "header.free_of": {"pt": "<b>{free}</b> livres de {total} ({pct:.0f}% em uso)",
                       "es": "<b>{free}</b> libres de {total} ({pct:.0f}% en uso)",
                       "en": "<b>{free}</b> free of {total} ({pct:.0f}% used)"},
    "header.disk_na": {"pt": "disco indisponível", "es": "disco no disponible",
                       "en": "disk unavailable"},
    "header.disk_of": {"pt": "Disco de: {target}",
                       "es": "Disco de: {target}",
                       "en": "Disk of: {target}"},

    # ------------------------------------------------------------ Console
    "console.title": {"pt": "CONSOLE", "es": "CONSOLA", "en": "CONSOLE"},
    "console.clear": {"pt": "Limpar", "es": "Limpiar", "en": "Clear"},
    "console.stop": {"pt": "Parar", "es": "Detener", "en": "Stop"},
    "console.stop_tip": {"pt": "Interrompe o comando em execução (e o yt-dlp dele)",
                         "es": "Detiene el comando en ejecución (y su yt-dlp)",
                         "en": "Stop the running command (and its yt-dlp)"},
    "console.hide": {"pt": "Ocultar", "es": "Ocultar", "en": "Hide"},
    "console.show": {"pt": "Mostrar", "es": "Mostrar", "en": "Show"},
    "console.placeholder": {"pt": "A saída dos comandos aparece aqui em "
                                  "tempo real...",
                            "es": "La salida de los comandos aparece aquí en "
                                  "tiempo real...",
                            "en": "Command output appears here in real time..."},
    # --------------------------------------------------- Widgets & logs
    "widget.ext_tip": {"pt": "Extensão: {name}", "es": "Extensión: {name}",
                       "en": "Extension: {name}"},
    "widget.ext_error": {"pt": "{name}\n\n{error}", "es": "{name}\n\n{error}",
                         "en": "{name}\n\n{error}"},
    "dash.btn_check": {"pt": "Verificar canais (check)",
                       "es": "Comprobar canales (check)",
                       "en": "Check channels (check)"},
    "dash.btn_mass": {"pt": "Mass archive (toda a lista)",
                      "es": "Mass archive (toda la lista)",
                      "en": "Mass archive (whole list)"},
    "dash.btn_mass_tip": {"pt": "Abre o diálogo de Mass archive da página Em massa",
                          "es": "Abre el diálogo de Mass archive de la página En masa",
                          "en": "Opens the Mass archive dialog from the Bulk page"},
    "dash.tool_ok": {"pt": "{name} ✓ instalado", "es": "{name} ✓ instalado",
                     "en": "{name} ✓ installed"},
    "dash.tool_missing": {"pt": "{name} ✗ ausente/fora do PATH",
                          "es": "{name} ✗ ausente/fuera del PATH",
                          "en": "{name} ✗ missing/not in PATH"},
    "dash.ext_refresh": {"pt": "atualiza a cada {refresh}s",
                         "es": "actualiza cada {refresh}s",
                         "en": "updates every {refresh}s"},
    "dash.dirs_hint": {"pt": "Duplo clique numa pasta para abrí-la na aba Organizar",
                       "es": "Doble clic en una carpeta para abrirla en Organizar",
                       "en": "Double-click a folder to open it in Organize"},
    "themes.log_applied": {"pt": "[tema] aplicado: {id}\n",
                           "es": "[tema] aplicado: {id}\n",
                           "en": "[theme] applied: {id}\n"},
    "profiles.log_created": {"pt": "[perfis] criado: {path}\n",
                             "es": "[perfis] creado: {path}\n",
                             "en": "[profiles] created: {path}\n"},
    "profiles.log_deleted": {"pt": "[perfis] excluído: {name}\n",
                             "es": "[perfis] eliminado: {name}\n",
                             "en": "[profiles] deleted: {name}\n"},
    "profiles.log_active": {"pt": "\n[perfil ativo: {name}]\n",
                            "es": "\n[perfil activo: {name}]\n",
                            "en": "\n[active profile: {name}]\n"},
    "ext.log_reloaded": {"pt": "[extensões] recarregadas\n",
                         "es": "[extensiones] recargadas\n",
                         "en": "[extensions] reloaded\n"},
    "ext.files_row": {"pt": "{name}  ({id}){flag}", "es": "{name}  ({id}){flag}",
                      "en": "{name}  ({id}){flag}"},
    "ext.details_file": {"pt": "Arquivo: {path}\nOnde: {where} • Atualiza a cada "
                               "{refresh}s • {estado}\nÚltimo valor: {last}",
                         "es": "Archivo: {path}\nDónde: {where} • Actualiza cada "
                               "{refresh}s • {estado}\nÚltimo valor: {last}",
                         "en": "File: {path}\nWhere: {where} • Updates every "
                               "{refresh}s • {estado}\nLast value: {last}"},
    "ext.details_error": {"pt": "\nErro: {error}", "es": "\nError: {error}",
                          "en": "\nError: {error}"},

    # ------------------------------------------------------- Comunes
    "btn.browse": {"pt": "Procurar...", "es": "Examinar...", "en": "Browse..."},
    "btn.save": {"pt": "Salvar", "es": "Guardar", "en": "Save"},
    "btn.reload": {"pt": "Recarregar", "es": "Recargar", "en": "Reload"},
    "busy.title": {"pt": "Ocupado", "es": "Ocupado", "en": "Busy"},
    "busy.text": {"pt": "Já existe um comando em execução (veja o Console).",
                  "es": "Ya hay un comando en ejecución (mira la Consola).",
                  "en": "A command is already running (see the Console)."},

    # ------------------------------------------------------------ Ajustes
    "settings.lang_title": {"pt": "Idioma", "es": "Idioma", "en": "Language"},
    "settings.lang_label": {"pt": "Idioma da interface:",
                            "es": "Idioma de la interfaz:",
                            "en": "Interface language:"},
    "settings.lang_note": {
        "pt": "Muda todos os textos da interface na hora. A escolha fica "
              "salva em config/gui_state.env (GUI_LANG) e vale para as "
              "próximas aberturas. O idioma não muda os scripts do backend "
              "(Bash) — eles continuam em ingles.",
        "es": "Cambia todos los textos de la interfaz al instante. La "
              "elección se guarda en config/gui_state.env (GUI_LANG) y "
              "aplica en las próximas aperturas. El idioma no cambia los "
              "scripts del backend (Bash) — siguen en ingles.",
        "en": "Switches the whole interface language instantly. The choice "
              "is saved to config/gui_state.env (GUI_LANG) and applies on "
              "next launches. The backend scripts (Bash) stay in english."},
    "settings.lang_changed": {"pt": "Idioma alterado para {lang} ✓ "
                                    "(aplicado agora e salvo)",
                              "es": "Idioma cambiado a {lang} ✓ "
                                    "(aplicado ahora y guardado)",
                              "en": "Language changed to {lang} ✓ "
                                    "(applied now and saved)"},
    "settings.title": {"pt": "Ajustes", "es": "Ajustes", "en": "Settings"},
    "settings.scope": {"pt": "origem: {scope}", "es": "origen: {scope}",
                       "en": "origin: {scope}"},
    "settings.scope_tip": {"pt": "Nível de CHANNELS_ROOT",
                           "es": "Nivel de CHANNELS_ROOT",
                           "en": "CHANNELS_ROOT level"},
    "settings.active_profile": {"pt": "perfil ativo: {name}",
                                "es": "perfil activo: {name}",
                                "en": "active profile: {name}"},
    "settings.channels_title": {"pt": "Pasta dos canais (onde ficam os downloads)",
                                "es": "Carpeta de canales (donde viven las descargas)",
                                "en": "Channel folder (where downloads live)"},
    "settings.path_placeholder": {
        "pt": "Ex: /run/media/flucio/MeuHDD/vonvakvas  (vazio = padrão do projeto)",
        "es": "Ej: /run/media/flucio/MeuHDD/vonvakvas  (vacío = config. por defecto del proyecto)",
        "en": "e.g. /run/media/flucio/MyHDD/vonvakvas  (empty = project default)"},
    "settings.btn_reset": {"pt": "Limpar (usar padrão do projeto)",
                           "es": "Limpiar (usar defecto del proyecto)",
                           "en": "Clear (use project default)"},
    "settings.btn_open": {"pt": "Abrir pasta", "es": "Abrir carpeta",
                          "en": "Open folder"},
    "settings.note": {
        "pt": "Onde os canais são baixados (cwd dos comandos archive/mass). "
              "Com um perfil ativo, o caminho é salvo no settings.env DELE — "
              "cada perfil pode apuntar a uma pasta/dispositivo diferente "
              "(útil para separar streams, jogos, etc. em discos distintos). "
              "Se a pasta tiver uma subpasta config/, os arquivos de lá têm "
              "prioridade sobre o config/ do projeto (fallback por arquivo).",
        "es": "Dónde se descargan los canales (cwd de los comandos archive/mass). "
              "Con un perfil activo, la ruta se guarda en el settings.env DE ÉL — "
              "cada perfil puede apuntar a una carpeta/dispositivo distinta "
              "(útil para separar streams, juegos, etc. en discos diferentes). "
              "Si la carpeta tiene una subcarpeta config/, los archivos de allí "
              "tienen prioridad sobre el config/ del proyecto (fallback por archivo).",
        "en": "Where channels are downloaded (cwd of archive/mass commands). "
              "With an active profile, the path is saved in ITS settings.env — "
              "each profile can point to a different folder/device "
              "(handy to split streams, games, etc. across disks). "
              "If the folder has a config/ subfolder, those files take "
              "priority over the project config/ (per-file fallback)."},
    "settings.origins_title": {"pt": "De onde vem cada arquivo de config (escopo ativo)",
                               "es": "De dónde viene cada archivo de config (ámbito activo)",
                               "en": "Where each config file comes from (active scope)"},
    "settings.btn_create_cfg": {"pt": "Criar config/ na pasta dos canais",
                                "es": "Crear config/ en la carpeta de canales",
                                "en": "Create config/ in the channel folder"},
    "settings.btn_copy_cfg": {"pt": "Copiar configs do projeto pra lá",
                              "es": "Copiar configs del proyecto hacia allá",
                              "en": "Copy project configs there"},
    "settings.origin.profile": {"pt": "perfil", "es": "perfil", "en": "profile"},
    "settings.origin.root": {"pt": "pasta dos canais", "es": "carpeta de canales",
                             "en": "channel folder"},
    "settings.origin.project": {"pt": "projeto", "es": "proyecto",
                                "en": "project"},
    "settings.exists": {"pt": "✓", "es": "✓", "en": "✓"},
    "settings.missing": {"pt": "✗ ausente", "es": "✗ ausente",
                         "en": "✗ missing"},
    "settings.saved": {"pt": "Configuração salva ✓ (escopo: {scope}; vale já "
                              "pro próximo comando)",
                       "es": "Configuración guardada ✓ (ámbito: {scope}; vale "
                             "ya para el próximo comando)",
                       "en": "Configuration saved ✓ (scope: {scope}; applies "
                             "to the next command already)"},
    "settings.scope_profile": {"pt": "perfil", "es": "perfil", "en": "profile"},
    "settings.scope_project": {"pt": "projeto", "es": "proyecto",
                               "en": "project"},
    "settings.scope_default": {"pt": "padrão do projeto", "es": "predeterminado del proyecto",
                               "en": "project default"},
    "settings.cleared": {"pt": "CHANNELS_ROOT limpo no escopo ativo",
                         "es": "CHANNELS_ROOT limpio en el ámbito activo",
                         "en": "CHANNELS_ROOT cleared in the active scope"},
    "settings.default_profile": {"pt": "padrão do projeto",
                                 "es": "config. por defecto del proyecto",
                                 "en": "default project config"},
    "settings.root_status": {"pt": "Pasta dos canais: {root}",
                             "es": "Carpeta de canales: {root}",
                             "en": "Channel folder: {root}"},
    "settings.pick_folder": {"pt": "Escolher a pasta dos canais (HDD externo)",
                             "es": "Elegir la carpeta de canales (HDD externo)",
                             "en": "Choose the channels folder (external HDD)"},
    "settings.folder_missing_title": {"pt": "Pasta não existe",
                                      "es": "La carpeta no existe",
                                      "en": "Folder does not exist"},
    "settings.folder_missing_text": {
        "pt": "'{path}' não existe ainda.\nSalvar assim mesmo? "
              "(a GUI volta pro padrão até a pasta existir)",
        "es": "'{path}' aún no existe.\n¿Guardar igualmente? "
              "(la GUI vuelve al defecto hasta que la carpeta exista)",
        "en": "'{path}' does not exist yet.\nSave anyway? "
              "(the GUI falls back to default until the folder exists)"},
    "settings.warn_valid_dir": {"pt": "Configure uma pasta válida antes.",
                                "es": "Configura una carpeta válida primero.",
                                "en": "Set a valid folder first."},
    "settings.copied": {"pt": "Copiados para a pasta:\n• ",
                        "es": "Copiados a la carpeta:\n• ",
                        "en": "Copied to the folder:\n• "},
    "settings.copied_none": {"pt": "Nada a copiar — tudo já existe lá.",
                             "es": "Nada que copiar — ya existe todo allí.",
                             "en": "Nothing to copy — everything already exists."},
    # ----------------------------------------------------------- Dashboard
    "dash.stats.channels": {"pt": "Canais na lista", "es": "Canales en la lista",
                            "en": "Channels in the list"},
    "dash.sub.channels": {"pt": "channel_list.txt efetiva",
                          "es": "channel_list.txt efectiva",
                          "en": "effective channel_list.txt"},
    "dash.stats.videos": {"pt": "Vídeos arquivados", "es": "Videos archivados",
                          "en": "Archived videos"},
    "dash.sub.videos": {"pt": "histórico do yt-dlp (archive.txt)",
                        "es": "histórico del yt-dlp (archive.txt)",
                        "en": "yt-dlp history (archive.txt)"},
    "dash.stats.saved": {"pt": "Canais salvos", "es": "Canales guardados",
                         "en": "Saved channels"},
    "dash.sub.saved": {"pt": "arquivados antes de caírem",
                       "es": "archivados antes de caer",
                       "en": "archived before falling"},
    "dash.stats.dirs": {"pt": "Pastas de canais", "es": "Carpetas de canales",
                        "en": "Channel folders"},
    "dash.sub.dirs": {"pt": "pasta configurada nos Ajustes",
                      "es": "carpeta configurada en Ajustes",
                      "en": "folder set in Settings"},
    "dash.stats.disk": {"pt": "Espaço livre no disco", "es": "Espacio libre en disco",
                        "en": "Free disk space"},
    "dash.sub.disk": {"pt": "dispositivo da pasta dos canais",
                      "es": "dispositivo de la carpeta de canales",
                      "en": "channel folder device"},
    "dash.stats.profile": {"pt": "Perfil ativo", "es": "Perfil activo",
                           "en": "Active profile"},
    "dash.sub.profile": {"pt": "troque no header ou em Perfis",
                         "es": "cámbialo en el header o en Perfiles",
                         "en": "change it in the header or Profiles"},
    "dash.ext_card": {"pt": "Extensões", "es": "Extensiones", "en": "Extensions"},
    "dash.tools": {"pt": "Ferramentas & Configuração", "es": "Herramientas & Configuración",
                   "en": "Tools & Configuration"},
    "dash.open_workdir": {"pt": "Abrir pasta dos canais",
                          "es": "Abrir carpeta de canales",
                          "en": "Open channels folder"},
    "dash.open_workdir_tip": {"pt": "Abre a pasta configurada no gerenciador de arquivos",
                              "es": "Abre la carpeta configurada en el gestor de archivos",
                              "en": "Opens the configured folder in the file manager"},
    "dash.quick_card": {"pt": "Ações rápidas", "es": "Acciones rápidas",
                        "en": "Quick actions"},
    "dash.btn_monitor": {"pt": "Abrir página Monitor", "es": "Abrir página Monitor",
                         "en": "Open Monitor page"},
    "dash.quick_note": {"pt": "O check testa HTTP de cada canal da lista e avisa no "
                              "Telegram se algum cair.",
                        "es": "El check prueba HTTP de cada canal de la lista y avisa por "
                              "Telegram si alguno cae.",
                        "en": "Check tests HTTP of each channel in the list and alerts "
                              "on Telegram if any goes down."},
    "dash.dirs_em": {"pt": "em: {dir}", "es": "en: {dir}", "en": "in: {dir}"},
    "dash.profile_default": {"pt": "padrão", "es": "predeterminado",
                             "en": "default"},
    "dash.disk_total": {"pt": "{total} totais • {pct}% em uso",
                        "es": "{total} totales • {pct}% en uso",
                        "en": "{total} total • {pct}% used"},
    "dash.dirs_hint_full": {"pt": "Pasta atual: {dir}\nDuplo clique: enviar para a "
                                  "página Organizar (mude em Ajustes se os canais "
                                  "ficam no HDD externo)",
                            "es": "Carpeta actual: {dir}\nDoble clic: enviar a la "
                                  "página Organizar (cambia en Ajustes si los canales "
                                  "están en el HDD externo)",
                            "en": "Current folder: {dir}\nDouble-click: send to the "
                                  "Organize page (change in Settings if channels live "
                                  "on the external HDD)"},
    "dash.dirs_card": {"pt": "Pastas de canais", "es": "Carpetas de canales",
                       "en": "Channel folders"},
    "dash.dirs_empty": {"pt": "(vazio — nenhún canal baixado ainda)",
                        "es": "(vacío — ningún canal descargado aún)",
                        "en": "(empty — no channel downloaded yet)"},
    # ------------------------------------------------------------- Arquivar
    "archive.title": {"pt": "Baixar canal do YouTube",
                      "es": "Descargar canal de YouTube",
                      "en": "Download YouTube channel"},
    "archive.canal_label": {"pt": "Canal:", "es": "Canal:", "en": "Channel:"},
    "archive.placeholder": {"pt": "@handle ou nome do canal (ex: lofigirl)",
                            "es": "@handle o nombre del canal (ej: lofigirl)",
                            "en": "@handle or channel name (e.g. lofigirl)"},
    "archive.mode_label": {"pt": "Modo:", "es": "Modo:", "en": "Mode:"},
    "archive.mode_n": {"pt": "Não contar visualização (sem cookies; não marca como assistido)",
                       "es": "No contar visualización (sin cookies; no marca como visto)",
                       "en": "Don't count view (no cookies; won't mark as watched)"},
    "archive.mode_y": {"pt": "Usar cookies (conta aleatória entre as contas 1, 2 e 3)",
                       "es": "Usar cookies (cuenta aleatoria entre las cuentas 1, 2 y 3)",
                       "en": "Use cookies (random account among accounts 1, 2, 3)"},
    "archive.tooltip": {"pt": "Sorteia uma das 3 contas configuradas (cookies_1/2/3.txt) para evitar bloqueios",
                        "es": "Elige una de las 3 cuentas configuradas (cookies_1/2/3.txt) para evitar bloqueos",
                        "en": "Picks one of the 3 configured accounts (cookies_1/2/3.txt) to avoid blocks"},
    "archive.btn_normal": {"pt": "Baixar (archive)", "es": "Descargar (archive)",
                           "en": "Download (archive)"},
    "archive.btn_playlist": {  # ntsp = nts playlist
                            "pt": "Baixar Playlist (archive-playlist)",
                            "es": "Descargar Playlist (archive-playlist)",
                            "en": "Download Playlist (archive-playlist)"},
    "archive.warn_title": {"pt": "Arquivar", "es": "Archivar", "en": "Archive"},
    "archive.warn_no_canal": {"pt": "Digite o @ do canal primeiro.",
                              "es": "Escribe el @ del canal primero.",
                              "en": "Type the channel @ first."},
    "archive.note_line1": {"pt": "• archive: yt-dlp até 720p, mp4, "
                                 "thumbnails/descrições/info.json, histórico no "
                                 "archive.txt efetivo",
                           "es": "• archive: yt-dlp hasta 720p, mp4, "
                                 "thumbnails/descripciones/info.json, histórico en "
                                 "el archive.txt efectivo",
                           "en": "• archive: yt-dlp up to 720p, mp4, "
                                 "thumbnails/descriptions/info.json, history in "
                                 "the effective archive.txt"},
    "archive.note_line2": {"pt": "• archive-playlist (ntsp = nts playlist): "
                                 "variante alternativa — acepta handle ou URL completa do canal",
                           "es": "• archive-playlist (ntsp = nts playlist): "
                                 "variante alternativa — acepta handle o URL completa del canal",
                           "en": "• archive-playlist (ntsp = nts playlist): "
                                 "alternative variant — accepts handle or full channel URL"},
    "archive.note_line3": {"pt": "• Com cookies: sorteia uma das 3 contas "
                                 "(cookies_1/2/3.txt); sem cookies: os vídeos não "
                                 "são marcados como assistidos",
                           "es": "• Con cookies: elige una de las 3 cuentas "
                                 "(cookies_1/2/3.txt); sin cookies: los videos no "
                                 "se marcan como vistos",
                           "en": "• With cookies: picks one of the 3 accounts "
                                 "(cookies_1/2/3.txt); without: videos aren't "
                                 "marked as watched"},
    "archive.note_perfil": {"pt": "• Perfil: {perfil} • Destino: {destino}",
                            "es": "• Perfil: {perfil} • Destino: {destino}",
                            "en": "• Profile: {perfil} • Destination: {destino}"},
    "common.default_profile": {"pt": "padrão do projeto",
                               "es": "config. por defecto del proyecto",
                               "en": "default project config"},
    # ------------------------------------------------------------ Organizar
    "org.path_title": {"pt": "Pasta alvo", "es": "Carpeta objetivo",
                       "en": "Target folder"},
    "org.btn_basedir": {"pt": "Pasta dos canais", "es": "Carpeta de canales",
                        "en": "Channels folder"},
    "org.btn_basedir_tip": {"pt": "Voltar para a pasta configurada nos Ajustes",
                            "es": "Volver a la carpeta configurada en Ajustes",
                            "en": "Go back to the folder set in Settings"},
    "org.actions_title": {"pt": "Ações", "es": "Acciones", "en": "Actions"},
    "org.ai_organize": {"pt": "Organizar (organize)", "es": "Organizar (organize)",
                        "en": "Organize (organize)"},
    "org.ai_instagram": {"pt": "Instagram (sem pfp)", "es": "Instagram (sin pfp)",
                         "en": "Instagram (no pfp)"},
    "org.ai_music": {"pt": "Músicas (organize-music)",
                     "es": "Música (organize-music)",
                     "en": "Music (organize-music)"},
    "org.ai_desorganize": {"pt": "Desorganizar (reverter)",
                           "es": "Desorganizar (revertir)",
                           "en": "Disorganize (undo)"},
    "org.ai_desorganize_music": {"pt": "Reverter músicas",
                                 "es": "Revertir música",
                                 "en": "Undo music"},
    "org.ai_prepare": {"pt": "Preparar upload IA (prep)",
                       "es": "Preparar subida a IA (prep)",
                       "en": "Prepare IA upload (prep)"},
    "org.note": {
        "pt": "• organize separa em descricao/ info_json/ thumbs/ pfp/ videos/\n"
              "• prepare-upload cria ia/ + ia/Videos + itemimage (exige pasta "
              "já organizada; avisa se faltar subpasta)\n"
              "• mass-organize ignora pastas listadas em .dirignore",
        "es": "• organize separa en descripcion/ info_json/ thumbs/ pfp/ videos/\n"
              "• prepare-upload crea ia/ + ia/Videos + itemimage (exige carpeta "
              "ya organizada; avisa si falta alguna subcarpeta)\n"
              "• mass-organize ignora carpetas listadas en .dirignore",
        "en": "• organize splits into descripcion/ info_json/ thumbs/ pfp/ videos/\n"
              "• prepare-upload creates ia/ + ia/Videos + itemimage (needs an "
              "organized folder; warns if a subfolder is missing)\n"
              "• mass-organize skips folders listed in .dirignore"},
    "org.empty": {"pt": "(vazio)", "es": "(vacío)", "en": "(empty)"},
    "org.hint": {"pt": "Clique numa pasta de canal para selecioná-la acima. "
                       "Pasta base: {dir}",
                 "es": "Haz clic en una carpeta de canal para seleccionarla "
                       "arriba. Carpeta base: {dir}",
                 "en": "Click a channel folder to select it above. "
                       "Base folder: {dir}"},
    "org.pick_title": {"pt": "Escolher pasta", "es": "Elegir carpeta",
                       "en": "Choose folder"},
    # ------------------------------------------------------------- Upload
    "upload.path_title": {"pt": "Pasta do canal (precisa ter ia/)",
                          "es": "Carpeta del canal (debe tener ia/)",
                          "en": "Channel folder (must have ia/)"},
    "upload.valid_na": {"pt": "ia/ não verificada", "es": "ia/ no verificada",
                        "en": "ia/ not checked"},
    "upload.valid_ok": {"pt": "ia/ encontrada — pronto para upload",
                        "es": "ia/ encontrada — lista para subir",
                        "en": "ia/ found — ready to upload"},
    "upload.valid_bad": {"pt": "ia/ ausente — rode organize + prepare-upload nessa pasta",
                         "es": "ia/ ausente — ejecuta organize + prepare-upload en esa carpeta",
                         "en": "ia/ missing — run organize + prepare-upload there"},
    "upload.up_title": {"pt": "Internet Archive", "es": "Internet Archive",
                        "en": "Internet Archive"},
    "upload.url_label": {"pt": "URL do canal:", "es": "URL del canal:",
                         "en": "Channel URL:"},
    "upload.btn_upload": {"pt": "Fazer upload para o Internet Archive",
                          "es": "Subir al Internet Archive",
                          "en": "Upload to the Internet Archive"},
    "upload.note": {
        "pt": "• Identifier do item: <pasta>-<data> (ex: canalasmr-2026-09-04)\n"
              "• Metadados automáticos: channel, creator, title, "
              "collection:opensource_movies, mediatype:movies, subject:asmr\n"
              "• Requer a CLI `ia` instalada e logada (ia configure)\n"
              "• A confirmação do script é respondida automaticamente pela GUI",
        "es": "• Identifier del item: <carpeta>-<fecha> (ej: canalasmr-2026-09-04)\n"
              "• Metadatos automáticos: channel, creator, title, "
              "collection:opensource_movies, mediatype:movies, subject:asmr\n"
              "• Requiere la CLI `ia` instalada y con sesión (ia configure)\n"
              "• Al confirmación del script la responde la GUI automáticamente",
        "en": "• Item identifier: <folder>-<date> (e.g. canalasmr-2026-09-04)\n"
              "• Automatic metadata: channel, creator, title, "
              "collection:opensource_movies, mediatype:movies, subject:asmr\n"
              "• Requires the `ia` CLI installed and logged in (ia configure)\n"
              "• Script confirmation is answered automatically by the GUI"},
    "upload.title": {"pt": "Upload", "es": "Subida", "en": "Upload"},
    "upload.pick_title": {"pt": "Escolher pasta do canal",
                          "es": "Elegir carpeta del canal",
                          "en": "Choose channel folder"},
    "upload.warn_no_folder": {"pt": "Escolha uma pasta válida.",
                              "es": "Elige una carpeta válida.",
                              "en": "Choose a valid folder."},
    "upload.warn_no_ia": {"pt": "'{pasta}/ia' não existe.\nRode organize + prepare-upload primeiro.",
                          "es": "'{pasta}/ia' no existe.\nEjecuta organize + prepare-upload primero.",
                          "en": "'{pasta}/ia' does not exist.\nRun organize + prepare-upload first."},
    "upload.warn_no_url": {"pt": "Informe a URL do canal (vai nos metadados do item).",
                           "es": "Indica la URL del canal (va en los metadatos del item).",
                           "en": "Provide the channel URL (goes in the item metadata)."},
    # ------------------------------------------------------------- Monitor
    "mon.total_title": {"pt": "Canais monitorados", "es": "Canales monitoreados",
                        "en": "Monitored channels"},
    "mon.total_sub": {"pt": "channel_list.txt efetiva",
                      "es": "channel_list.txt efectiva",
                      "en": "effective channel_list.txt"},
    "mon.saved_title": {"pt": "Salvos antes de cair",
                        "es": "Guardados antes de caer",
                        "en": "Saved before falling"},
    "mon.saved_sub": {"pt": "succeeded_archvings.txt",
                      "es": "succeeded_archvings.txt",
                      "en": "succeeded_archvings.txt"},
    "mon.list_title": {"pt": "Canais da lista", "es": "Canales de la lista",
                       "en": "Channels in the list"},
    "mon.actions_title": {"pt": "Ações", "es": "Acciones", "en": "Actions"},
    "mon.btn_check": {"pt": "Verificar canais agora (check)",
                      "es": "Comprobar canales ahora (check)",
                      "en": "Check channels now (check)"},
    "mon.btn_refresh": {"pt": "Recarregar lista", "es": "Recargar lista",
                        "en": "Reload list"},
    "mon.known": {
        "pt": "Erro conhecido (errors-exp/erros.txt): se o canal estiver em LIVE "
              "no momento do archive, o yt-dlp solta um monte de linhas do "
              "googlevideo.com — ou espera a live, ou comenta o canal na "
              "channel_list.txt temporariamente. Vídeos member-only também dão erro.",
        "es": "Error conocido (errors-exp/erros.txt): si el canal está en LIVE "
              "durante el archive, el yt-dlp suelta montones de líneas de "
              "googlevideo.com — o esperas la live, o comentas el canal en "
              "channel_list.txt temporalmente. Los videos solo-miembros también fallan.",
        "en": "Known error (errors-exp/erros.txt): if the channel is LIVE while "
              "archiving, yt-dlp spits out lots of googlevideo.com lines — either "
              "wait for the live to end, or comment the channel in "
              "channel_list.txt temporarily. Member-only videos also fail."},
    "mon.empty": {"pt": "(lista vazia)", "es": "(lista vacía)",
                  "en": "(empty list)"},
    "mon.hint": {"pt": "Perfil: {perfil} • O check testa HTTP 200 de cada canal "
                        "(com pausa de 0.5s) e manda alerta no Telegram se algum "
                        "estiver fora do ar.",
                 "es": "Perfil: {perfil} • El check prueba HTTP 200 de cada canal "
                       "(con pausa de 0.5s) y envía alerta por Telegram si alguno "
                       "está caído.",
                 "en": "Profile: {perfil} • Check tests HTTP 200 of each channel "
                       "(with a 0.5s pause) and sends a Telegram alert if any is "
                       "down."},
    # ------------------------------------------------------------- Em massa
    "mass.warn_title": {"pt": "Atenção", "es": "Atención", "en": "Warning"},
    "mass.warn_chip1": {"pt": "operações longas", "es": "operaciones largas",
                        "en": "long operations"},
    "mass.warn_chip2": {"pt": "toda a lista de canais",
                        "es": "toda la lista de canales",
                        "en": "the whole channel list"},
    "mass.actions_title": {"pt": "Comandos", "es": "Comandos",
                           "en": "Commands"},
    "mass.btn_archive": {"pt": "Mass archive (baixar toda a lista)",
                         "es": "Mass archive (bajar toda la lista)",
                         "en": "Mass archive (download whole list)"},
    "mass.btn_organize": {"pt": "Mass organize (organizar tudo)",
                          "es": "Mass organize (organizar todo)",
                          "en": "Mass organize (organize all)"},
    "mass.box_cookies": {"pt": "Com cookies (conta aleatória)",
                         "es": "Con cookies (cuenta aleatoria)",
                         "en": "With cookies (random account)"},
    "mass.box_ghost": {"pt": "Sem cookies (não contar visualização)",
                       "es": "Sin cookies (no contar visualización)",
                       "en": "Without cookies (don't count views)"},
    "mass.box_cancel": {"pt": "Cancelar", "es": "Cancelar", "en": "Cancel"},
    "mass.organize_q_title": {"pt": "Mass organize", "es": "Mass organize",
                              "en": "Mass organize"},
    "mass.organize_q": {"pt": "Organizar todas as pastas de canais?\n"
                               "(Respeita o .dirignore se existir)",
                        "es": "¿Organizar todas las carpetas de canales?\n"
                              "(Respeta el .dirignore si existe)",
                        "en": "Organize all channel folders?\n"
                              "(Respects .dirignore if present)"},
    "mass.box_title": {"pt": "Mass archive", "es": "Mass archive",
                       "en": "Mass archive"},
    "mass.box_text": {"pt": "Baixar os {n} canais da lista agora?\n"
                             "O processo roda com intervalos aleatórios e pode "
                             "levar horas.\nAcompanhe a saída no Console.",
                      "es": "¿Descargar los {n} canales de la lista ahora?\n"
                            "El proceso corre con intervalos aleatorios y puede "
                            "llevar horas.\nSigue la salida en la Consola.",
                      "en": "Download the {n} channels from the list now?\n"
                            "It runs with random intervals and may take hours.\n"
                            "Follow the output in the Console."},
    "mass.warn_text": {"pt": "Esses comandos processam TODOS os canais da "
                              "channel_list.txt efetiva (perfil: {perfil}).\n"
                              "• mass-archive: baixa canal por canal, com sleep "
                              "aleatório anti-bloqueio entre downloads — pode "
                              "levar horas.\n"
                              "• mass-organize: organiza todas as pastas do "
                              "diretório atual (respeita .dirignore).\n"
                              "• Dica: se um canal estiver em live, comente ele "
                              "na channel_list.txt antes (veja errors-exp/erros.txt).",
                       "es": "Estos comandos procesan TODOS los canales de la "
                             "channel_list.txt efectiva (perfil: {perfil}).\n"
                             "• mass-archive: descarga canal por canal, con sleep "
                             "aleatorio anti-bloqueo entre descargas — puede "
                             "llevar horas.\n"
                             "• mass-organize: organiza todas las carpetas del "
                             "directorio actual (respeta .dirignore).\n"
                             "• Consejo: si un canal está en live, coméntalo en "
                             "channel_list.txt antes (ver errors-exp/erros.txt).",
                       "en": "These commands process ALL channels from the "
                             "effective channel_list.txt (profile: {perfil}).\n"
                             "• mass-archive: downloads channel by channel, with "
                             "random anti-block sleeps between downloads — may "
                             "take hours.\n"
                             "• mass-organize: organizes all folders in the "
                             "current directory (respects .dirignore).\n"
                             "• Tip: if a channel is live, comment it in "
                             "channel_list.txt first (see errors-exp/erros.txt)."},
    # ------------------------------------------------------------- Editor
    "editor.placeholder": {"pt": "Selecione um arquivo na lista à esquerda...",
                           "es": "Selecciona un archivo en la lista de la izquierda...",
                           "en": "Select a file from the list on the left..."},
    "editor.btn_to_profile": {"pt": "Copiar para o perfil",
                              "es": "Copiar al perfil",
                              "en": "Copy to profile"},
    "editor.btn_to_profile_tip": {
        "pt": "Copia o conteúdo exibido (ex: do config/ do projeto) para o "
              "perfil ativo — o perfil passa a ser a fonte da verdade.",
        "es": "Copia el contenido mostrado (ej: del config/ del proyecto) al "
              "perfil activo — el perfil pasa a ser la fuente de verdad.",
        "en": "Copies the displayed content (e.g. from project config/) to the "
              "active profile — the profile becomes the source of truth."},
    "editor.warn_read": {"pt": "Não consegui ler o arquivo:\n{exc}",
                         "es": "No pude leer el archivo:\n{exc}",
                         "en": "Could not read the file:\n{exc}"},
    "editor.source_none": {"pt": "nenhum arquivo", "es": "ningún archivo",
                           "en": "no file"},
    "editor.source_profile": {"pt": "perfil: {perfil}", "es": "perfil: {perfil}",
                              "en": "profile: {perfil}"},
    "editor.source_global": {"pt": "global (projeto)", "es": "global (proyecto)",
                             "en": "global (project)"},
    "editor.source_root": {"pt": "pasta dos canais", "es": "carpeta de canales",
                           "en": "channel folder"},
    "editor.title": {"pt": "Editor", "es": "Editor", "en": "Editor"},
    "editor.no_perfil": {"pt": "Nenhum perfil ativo — o arquivo já é o do projeto.",
                         "es": "Ningún perfil activo — el archivo ya es el del proyecto.",
                         "en": "No active profile — the file is already the project one."},
    "editor.already_profile": {"pt": "'{name}' já é do perfil ativo.",
                               "es": "'{name}' ya es del perfil activo.",
                               "en": "'{name}' already belongs to the active profile."},
    "editor.saved_status": {"pt": "Editor: {name} salvo ✓",
                            "es": "Editor: {name} guardado ✓",
                            "en": "Editor: {name} saved ✓"},
    "editor.saved_log": {"pt": "[editor] salvo: {path}\n",
                         "es": "[editor] guardado: {path}\n",
                         "en": "[editor] saved: {path}\n"},
    "editor.default": {"pt": "padrão",
                        "es": "predeterminado",
                        "en": "default"},
    "editor.will_be_created": {"pt": "  (será criado ao salvar)",
                                "es": "  (se creará al guardar)",
                                "en": "  (will be created on save)"},
    "editor.copied_to_profile": {"pt": "[editor] copiado para o perfil {perfil}: {dst}\n",
                                  "es": "[editor] copiado al perfil {perfil}: {dst}\n",
                                  "en": "[editor] copied to profile {perfil}: {dst}\n"},
    "editor.perfil_label": {"pt": "perfil",
                             "es": "perfil",
                             "en": "profile"},
    # ------------------------------------------------------------- Perfis
    "profiles.title": {"pt": "Perfis", "es": "Perfiles", "en": "Profiles"},
    "profiles.btn_activate": {"pt": "Tornar ativo", "es": "Activar",
                              "en": "Set active"},
    "profiles.btn_create": {"pt": "Criar perfil...", "es": "Crear perfil...",
                            "en": "Create profile..."},
    "profiles.btn_files": {"pt": "Ver arquivos", "es": "Ver archivos",
                           "en": "View files"},
    "profiles.btn_delete": {"pt": "Excluir", "es": "Eliminar",
                            "en": "Delete"},
    "profiles.help_title": {"pt": "Como funciona", "es": "Cómo funciona",
                            "en": "How it works"},
    "profiles.empty": {"pt": "(nenhum perfil — usando o config/ padrão)",
                       "es": "(ningún perfil — usando el config/ por defecto)",
                       "en": "(no profiles — using default config/)"},
    "profiles.active_chip": {"pt": "ativo: {name}", "es": "activo: {name}",
                             "en": "active: {name}"},
    "profiles.sel_first": {"pt": "Selecione um perfil na lista.",
                           "es": "Selecciona un perfil de la lista.",
                           "en": "Select a profile from the list."},
    "profiles.warn_running": {"pt": "Existe um comando em execução — espere terminar.",
                              "es": "Hay un comando en ejecución — espera a que termine.",
                              "en": "A command is running — wait for it to finish."},
    "profiles.create_title": {"pt": "Criar perfil", "es": "Crear perfil",
                              "en": "Create profile"},
    "profiles.create_label": {"pt": "Nome do perfil (ex: streams, jogos, asmr):",
                              "es": "Nombre del perfil (ej: streams, juegos, asmr):",
                              "en": "Profile name (e.g. streams, games, asmr):"},
    "profiles.create_q": {"pt": "Copiar a config base do projeto para o perfil?\n"
                                "(lista de canais, cookies e telegram.env — o "
                                "archive.txt fica vazio para o perfil ter "
                                "histórico próprio)",
                          "es": "¿Copiar la config base del proyecto al perfil?\n"
                                "(lista de canales, cookies y telegram.env — el "
                                "archive.txt queda vacío para que el perfil tenga "
                                "su propio histórico)",
                          "en": "Copy the project base config to the profile?\n"
                                "(channel list, cookies and telegram.env — "
                                "archive.txt stays empty so the profile keeps its "
                                "own history)"},
    "profiles.files_of": {"pt": "Arquivos do perfil:\n• ",
                          "es": "Archivos del perfil:\n• ",
                          "en": "Profile files:\n• "},
    "profiles.no_files": {"pt": "O perfil ainda não tem arquivos.",
                          "es": "El perfil aún no tiene archivos.",
                          "en": "The profile has no files yet."},
    "profiles.del_active": {"pt": "Este perfil está ativo.\nTroque para outro "
                                  "perfil antes de excluir.",
                            "es": "Este perfil está activo.\nCambia a otro "
                                  "perfil antes de eliminarlo.",
                            "en": "This profile is active.\nSwitch to another "
                                  "profile before deleting."},
    "profiles.del_title": {"pt": "Excluir perfil", "es": "Eliminar perfil",
                           "en": "Delete profile"},
    "profiles.del_q": {"pt": "Excluir o perfil '{name}' e TODOS os arquivos "
                              "dele?\nEssa ação não pode ser desfeita.",
                       "es": "¿Eliminar el perfil '{name}' y TODOS sus "
                             "archivos?\nEsta acción no se puede deshacer.",
                       "en": "Delete profile '{name}' and ALL its files?\n"
                             "This cannot be undone."},
    "profiles.del_fail": {"pt": "Não consegui excluir:\n{exc}",
                          "es": "No pude eliminar:\n{exc}",
                          "en": "Could not delete:\n{exc}"},
    "profiles.help_note": {
        "pt": "• Cada perfil é uma pasta em config/profiles/<nome>/ com arquivos "
              "próprios: channel_list.txt, cookies_1/2/3.txt, telegram.env, "
              "archive.txt e settings.env.\n"
              "• Ao criar, a GUI pode copiar a config base do projeto (menos o "
              "archive.txt — cada perfil mantém histórico próprio).\n"
              "• Com um perfil ativo, TODOS os comandos da GUI usam os arquivos "
              "dele (o que não existir no perfil cai no config/ do projeto — "
              "fallback por arquivo).\n"
              "• Cada perfil pode ter uma pasta de canais diferente "
              "(CHANNELS_ROOT próprio em settings.env — configure na aba Ajustes "
              "com o perfil ativo).\n"
              "• No terminal: VONVAKVAS_PROFILE=nome ./vonvakvas.sh <comando>\n"
              "• Uso típico: um perfil para streams, outro para jogos, outro "
              "para ASMR — cada um com sua lista e seu histórico.",
        "es": "• Cada perfil es una carpeta en config/profiles/<nombre>/ con "
              "archivos propios: channel_list.txt, cookies_1/2/3.txt, "
              "telegram.env, archive.txt y settings.env.\n"
              "• Al crearlo, la GUI puede copiar la config base del proyecto "
              "(menos el archive.txt — cada perfil mantiene su propio histórico).\n"
              "• Con un perfil activo, TODOS los comandos de la GUI usan sus "
              "archivos (lo que no exista en el perfil cae al config/ del "
              "proyecto — fallback por archivo).\n"
              "• Cada perfil puede tener una carpeta de canales distinta "
              "(CHANNELS_ROOT propio en settings.env — configúralo en Ajustes "
              "con el perfil activo).\n"
              "• En la terminal: VONVAKVAS_PROFILE=nombre ./vonvakvas.sh <comando>\n"
              "• Uso típico: un perfil para streams, otro para juegos, otro "
              "para ASMR — cada uno con su lista y su histórico.",
        "en": "• Each profile is a folder in config/profiles/<name>/ with its "
              "own files: channel_list.txt, cookies_1/2/3.txt, telegram.env, "
              "archive.txt and settings.env.\n"
              "• On creation the GUI can copy the project base config (except "
              "archive.txt — each profile keeps its own history).\n"
              "• With an active profile, ALL GUI commands use its files (what's "
              "missing in the profile falls back to project config/ — "
              "per-file fallback).\n"
              "• Each profile can point to a different channel folder "
              "(own CHANNELS_ROOT in settings.env — set it in Settings "
              "with the profile active).\n"
              "• In the terminal: VONVAKVAS_PROFILE=name ./vonvakvas.sh <command>\n"
              "• Typical use: one profile for streams, another for games, "
              "another for ASMR — each with its list and history."},
    # ------------------------------------------------------------- Temas
    "themes.title": {"pt": "Temas disponíveis", "es": "Temas disponibles",
                     "en": "Available themes"},
    "themes.btn_apply": {"pt": "Aplicar tema", "es": "Aplicar tema",
                         "en": "Apply theme"},
    "themes.btn_reload_tip": {"pt": "Relê gui/themes/ (para temas recém-criados)",
                              "es": "Relee gui/themes/ (para temas recién creados)",
                              "en": "Re-reads gui/themes/ (for newly created themes)"},
    "themes.btn_open": {"pt": "Abrir pasta de temas", "es": "Abrir carpeta de temas",
                        "en": "Open themes folder"},
    "themes.help_title": {"pt": "Criar um tema personalizado",
                          "es": "Crear un tema personalizado",
                          "en": "Create a custom theme"},
    "themes.no_desc": {"pt": "(sem descrição)", "es": "(sin descripción)",
                       "en": "(no description)"},
    "themes.active_chip": {"pt": "ativo: {theme}", "es": "activo: {theme}",
                           "en": "active: {theme}"},
    "themes.kind_url": {"pt": "URL", "es": "URL", "en": "URL"},
    "themes.kind_file": {"pt": "arquivo", "es": "archivo", "en": "file"},
    "themes.no_decor": {"pt": "sem decorações configuradas",
                        "es": "sin decoraciones configuradas",
                        "en": "no decorations configured"},
    "themes.applied": {"pt": "Tema '{id}' aplicado ✓ (salvo para as próximas aberturas)",
                       "es": "Tema '{id}' aplicado ✓ (guardado para las próximas aperturas)",
                       "en": "Theme '{id}' applied ✓ (saved for next launches)"},
    "themes.help_note": {
        "pt": "• Cada tema é um arquivo JSON em gui/themes/ — a GUI lista "
              "tudo que estiver lá, sem precisar registrar em código.\n"
              "• Não precisa definir todas as chaves: o que faltar herda o "
              "padrão. Um tema pode ser só 3 linhas mudando o acento.\n"
              "• Os fundos translúcidos dos chips são derivados das cores do "
              "tema automaticamente — qualquer tema fica consistente.\n"
              "• Documentação completa (formato, tokens, dicas de contraste): "
              "gui/themes/README.md",
        "es": "• Cada tema es un archivo JSON en gui/themes/ — la GUI lista "
              "todo lo que haya allí, sin registrarlo en código.\n"
              "• No hace falta definir todas las claves: lo que falte hereda "
              "el patrón. Un tema puede ser solo 3 líneas cambiando el acento.\n"
              "• Los fondos translúcidos de los chips se derivan de los colores "
              "del tema automáticamente — cualquier tema queda consistente.\n"
              "• Documentación completa (formato, tokens, consejos de "
              "contraste): gui/themes/README.md",
        "en": "• Each theme is a JSON file in gui/themes/ — the GUI lists "
              "everything there, no need to register in code.\n"
              "• You don't need to define every key: missing ones inherit the "
              "default. A theme can be just 3 lines changing the accent.\n"
              "• Translucent chip backgrounds are derived from the theme colors "
              "automatically — any theme stays consistent.\n"
              "• Full docs (format, tokens, contrast tips): gui/themes/README.md"},
    "themes.tok_bg": {"pt": "fundo", "es": "fondo", "en": "background"},
    "themes.tok_sidebar": {"pt": "sidebar", "es": "sidebar", "en": "sidebar"},
    "themes.tok_card": {"pt": "card", "es": "card", "en": "card"},
    "themes.tok_button": {"pt": "botão", "es": "botón", "en": "button"},
    "themes.tok_border": {"pt": "borda", "es": "borde", "en": "border"},
    "themes.tok_text": {"pt": "texto", "es": "texto", "en": "text"},
    "themes.tok_secondary": {"pt": "secundário", "es": "secundario",
                             "en": "secondary"},
    "themes.tok_accent": {"pt": "acento", "es": "acento", "en": "accent"},
    "themes.tok_ok": {"pt": "ok", "es": "ok", "en": "ok"},
    "themes.tok_error": {"pt": "erro", "es": "error", "en": "error"},
    "themes.tok_warning": {"pt": "aviso", "es": "aviso", "en": "warning"},
    "themes.tok_console": {"pt": "console", "es": "consola", "en": "console"},
    # ------------------------------------------------------- Extensiones
    "ext.title": {"pt": "Extensões carregadas", "es": "Extensiones cargadas",
                  "en": "Loaded extensions"},
    "ext.details_prompt": {"pt": "Selecione uma extensão para ver os detalhes.",
                           "es": "Selecciona una extensión para ver los detalles.",
                           "en": "Select an extension to see the details."},
    "ext.btn_toggle_off": {"pt": "Desativar", "es": "Desactivar",
                           "en": "Disable"},
    "ext.btn_toggle_on": {"pt": "Ativar", "es": "Activar", "en": "Enable"},
    "ext.btn_open": {"pt": "Abrir pasta", "es": "Abrir carpeta",
                     "en": "Open folder"},
    "ext.help_title": {"pt": "Criar uma extensão", "es": "Crear una extensión",
                       "en": "Create an extension"},
    "ext.disabled_suffix": {"pt": "  [desativada]", "es": "  [desactivada]",
                            "en": "  [disabled]"},
    "ext.count": {"pt": "{ativas} ativa(s) de {total}",
                  "es": "{ativas} activa(s) de {total}",
                  "en": "{ativas} active of {total}"},
    "ext.errors": {"pt": "Problemas ao carregar:\n• ",
                   "es": "Problemas al cargar:\n• ",
                   "en": "Problems loading:\n• "},
    "ext.state_active": {"pt": "ativa", "es": "activa", "en": "active"},
    "ext.state_disabled": {"pt": "desativada", "es": "desactivada",
                           "en": "disabled"},
    "ext.reload_tip": {"pt": "Re-escaneia gui/extensions/ (novos .py, mudanças)",
                       "es": "Re-escannea gui/extensions/ (nuevos .py, cambios)",
                       "en": "Re-scans gui/extensions/ (new .py files, changes)"},
    "ext.details": {"pt": "Arquivo: {path}\nOnde: {where} • Atualiza a cada "
                           "{refresh}s • {estado}\nÚltimo valor: {value}",
                    "es": "Archivo: {path}\nDónde: {where} • Actualiza cada "
                          "{refresh}s • {estado}\nÚltimo valor: {value}",
                    "en": "File: {path}\nWhere: {where} • Updates every "
                          "{refresh}s • {estado}\nLast value: {value}"},
    "ext.detail_error": {"pt": "\nErro: {error}", "es": "\nError: {error}",
                         "en": "\nError: {error}"},
    "ext.help_note": {
        "pt": "• Crie um .py em gui/extensions/ com NAME, WHERE e get_value().\n"
              "• WHERE = [\"header\"], [\"dashboard\"] ou os dois.\n"
              "• get_value() retorna (texto, estado) — estado: \"ok\", \"warn\", "
              "\"bad\" ou \"muted\" (cores do tema ativo).\n"
              "• REFRESH = segundos entre leituras (padrão 5; get_value deve "
              "ser rápido — roda na thread da interface).\n"
              "• Arquivos começando com \"_\" não são cargados (veja o "
              "_exemplo.py da pasta).\n"
              "• Erros ficam isolados: extensão quebrada aparece como \"erro\" "
              "ou é pulada, e a GUI segue de pé.\n"
              "• Documentação completa: gui/extensions/README.md",
        "es": "• Crea un .py en gui/extensions/ con NAME, WHERE y get_value().\n"
              "• WHERE = [\"header\"], [\"dashboard\"] o ambos.\n"
              "• get_value() devuelve (texto, estado) — estado: \"ok\", \"warn\", "
              "\"bad\" o \"muted\" (colores del tema activo).\n"
              "• REFRESH = segundos entre lecturas (por defecto 5; get_value "
              "debe ser rápido — corre en el hilo de la interfaz).\n"
              "• Los archivos que empiezan con \"_\" no se cargan (mira el "
              "_exemplo.py de la carpeta).\n"
              "• Los errores quedan aislados: una extensión rota aparece como "
              "\"error\" o se omite, y la GUI sigue en pie.\n"
              "• Documentación completa: gui/extensions/README.md",
        "en": "• Create a .py in gui/extensions/ with NAME, WHERE and get_value().\n"
              "• WHERE = [\"header\"], [\"dashboard\"] or both.\n"
              "• get_value() returns (text, state) — state: \"ok\", \"warn\", "
              "\"bad\" or \"muted\" (colors of the active theme).\n"
              "• REFRESH = seconds between reads (default 5; get_value must be "
              "fast — it runs on the UI thread).\n"
              "• Files starting with \"_\" are not loaded (see _exemplo.py in "
              "the folder).\n"
              "• Errors are isolated: a broken extension shows as \"error\" or "
              "is skipped, and the GUI stays up.\n"
              "• Full docs: gui/extensions/README.md"},
    # __CATALOG__
}

# ---------------------------------------------------------------------------
# Estado / persistência
# ---------------------------------------------------------------------------

_lang = DEFAULT_LANG
_persisted = False


def _load_persisted() -> int:
    """Lee GUI_LANG del gui_state.env (una sola vez). Devuelve el código."""
    global _persisted
    if _persisted:
        return -1
    _persisted = True
    if STATE_FILE.exists():
        for line in STATE_FILE.read_text(encoding="utf-8",
                                         errors="replace").splitlines():
            line = line.strip()
            if line.startswith("GUI_LANG"):
                _, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                if val in LANGUAGES:
                    return _set_lang_only(val)
    return -1


def _set_lang_only(code: str) -> int:
    global _lang
    if code in LANGUAGES:
        _lang = code
        return 1
    return -1


def _save(code: str) -> None:
    """Persiste GUI_LANG preservando las demás líneas del archivo."""
    lines: list[str]
    if STATE_FILE.exists():
        lines = STATE_FILE.read_text(encoding="utf-8",
                                     errors="replace").splitlines()
    else:
        lines = ["# Estado de la GUI (perfil / tema / idioma). "
                 "Archivo solo de la interfaz."]
    new_line = f'GUI_LANG="{code}"'
    for i, line in enumerate(lines):
        if line.strip().startswith("GUI_LANG"):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def current_lang() -> str:
    """Idioma activo (después de leer la preferencia persistida una vez)."""
    _load_persisted()
    return _lang


def tr(key: str, **fmt: object) -> str:
    """Texto para `key` en el idioma activo, con fallback a Português."""
    _load_persisted()
    entry = _T.get(key)
    if entry is None:
        return key
    txt = entry.get(_lang) or entry.get(DEFAULT_LANG) or key
    if fmt:
        try:
            txt = txt.format(**fmt)
        except (KeyError, IndexError):
            pass
    return txt


def set_language(code: str) -> None:
    """Cambia el idioma activo y lo persiste. Se aplica en vivo por la GUI."""
    global _lang
    if code not in LANGUAGES:
        code = DEFAULT_LANG
    _lang = code
    _save(code)


def languages() -> list[str]:
    """Códigos de idioma disponibles (orden canónico)."""
    return list(LANGUAGES.keys())