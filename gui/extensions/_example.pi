"""
EXEMPLO DE EXTENSOES COM INTERACOES

Este arquivo e um template (comeca com "_" entao e ignorado).
Copie para criar sua propria extensao.

Para testar: copie este arquivo sem o "_" no nome (ex: "meu_player.py")
e recarregue as extensoes na GUI.
"""

# Obrigatorio: nome exibido na GUI
NAME = "Player Exemplo"

# Obrigatorio: onde mostrar ("header", "dashboard" ou ambos)
WHERE = ["dashboard"]

# Opcional: segundos entre atualizacoes (padrao: 5)
REFRESH = 3

# Opcional: define botoes de interacao
INTERACTIONS = [
    {"id": "prev", "label": "prev", "tooltip": "Faixa anterior"},
    {"id": "play", "label": "play", "tooltip": "Tocar"},
    {"id": "pause", "label": "pause", "tooltip": "Pausar"},
    {"id": "next", "label": "next", "tooltip": "Proxima faixa"},
]

# Estado interno da extensao (opcional)
_is_playing = False
_current_track = "Nenhuma"


def get_value():
    """
    Obrigatorio: retorna o valor exibido na GUI.
    Deve ser rapido (<100ms) - roda na thread da interface.
    Retorna: (texto, estado) ou apenas texto
    """
    if _is_playing:
        return (f"Tocando: {_current_track}", "ok")
    return ("Parado", "muted")


def on_interaction(interaction_id: str, ext):
    """
    Opcional: chamado quando usuario clica em um botao.
    Recebe o id da acao e a extensao atual.
    Retorna opcionalmente (novo_texto, novo_estado) para atualizar o display.
    """
    global _is_playing, _current_track

    if interaction_id == "play":
        _is_playing = True
        _current_track = "Musica Exemplo"
        return ("Tocando: Musica Exemplo", "ok")

    elif interaction_id == "pause":
        _is_playing = False
        return ("Pausado", "warn")

    elif interaction_id == "prev":
        return ("Faixa anterior", "ok")

    elif interaction_id == "next":
        return ("Proxima faixa", "ok")

    return None
