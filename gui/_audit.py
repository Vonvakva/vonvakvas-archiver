import sys
sys.path.insert(0, ".")
import i18n

# Keys used by refactored widgets/pages
test_keys = [
    # widget.* (MetricChip / header ext chips)
    "widget.ext_tip", "widget.ext_error",
    # dash.* (dashboard retranslate)
    "dash.stats.channels", "dash.sub.channels", "dash.quick_card",
    "dash.btn_check", "dash.btn_mass", "dash.btn_mass_tip",
    "dash.btn_monitor", "dash.quick_note", "dash.dirs_em",
    "dash.profile_default", "dash.disk_total", "dash.dirs_hint_full",
    "dash.tool_ok", "dash.tool_missing", "dash.ext_refresh",
    "dash.open_workdir", "dash.open_workdir_tip",
    # profiles.* (profiles_page retranslate)
    "profiles.title", "profiles.btn_activate", "profiles.log_active",
    "profiles.log_created", "profiles.log_deleted",
    # themes.* (themes_page retranslate)
    "themes.title", "themes.btn_apply", "themes.log_applied",
    "themes.tok_bg", "themes.tok_console",
    # ext.* (extensions_page retranslate)
    "ext.title", "ext.files_row", "ext.count", "ext.details_file",
    "ext.log_reloaded",
]

fails = []
for lang in ["pt", "es", "en"]:
    i18n.set_language(lang)
    for key in test_keys:
        val = i18n.tr(key)
        if val == key:
            fails.append(f"{lang}: {key}")
    print(f"{lang}: {len(test_keys) - sum(1 for k in test_keys if i18n.tr(k) == k)}"
          f"/{len(test_keys)} keys OK")

if fails:
    print("\nFAILS:")
    for f in fails:
        print("  ✗ " + f)
    sys.exit(1)
print("\nALL i18n TESTS PASSED!")