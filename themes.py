"""
Theme configurations for the bingo app.
Each theme defines colors, messages, and visual elements.
"""

THEMES = {
    "alien": {
        "name": "Alien Invasion",
        "colors": {
            "background": "#1e2328",
            "text": "#e2fcff",
            "primary": "#7303c0",
            "secondary": "#18f2b2",
            "accent": "#b5179e",
            "tile_bg": "#1a1a1a",
            "tile_border": "#b5179e",
            "tile_revealed_text": "#ffffff",
            "neon_glow": "rgba(181, 23, 158, 0.7)",
            "grid": "rgba(115, 3, 192, 0.3)"
        },
        "messages": {
            "bingo": "BINGO!",
            "double_bingo": "DOUBLE BINGO!",
            "h_bingo": "H BINGO!",
            "super_bingo": "You are a God Gamer"
        },
        "emojis": {
            "confetti": ["🛸", "👽", "🌠", "🌌", "💫", "✨", "⭐", "🪐", "🔭", "🚀"],
            "decorations": ["🛸", "👽"],
            "button_randomize": "🎲",
            "button_reset": "↩️"
        },
        "fonts": {
            "primary": "Orbitron",
            "secondary": "Exo 2",
            "accent": "Audiowide"
        }
    },
    "ghost": {
        "name": "Ghost Hunt",
        "colors": {
            "background": "#1e2328",
            "text": "#e8e8e8",
            "primary": "#4a148c",
            "secondary": "#7b1fa2",
            "accent": "#ff6f00",
            "tile_bg": "#1a1a1a",
            "tile_border": "#ff6f00",
            "tile_revealed_text": "#ffffff",
            "neon_glow": "rgba(255, 111, 0, 0.7)",
            "grid": "rgba(74, 20, 140, 0.3)"
        },
        "messages": {
            "bingo": "BINGO!",
            "double_bingo": "DOUBLE BINGO!",
            "h_bingo": "H BINGO!",
            "super_bingo": "You are a God Gamer"
        },
        "emojis": {
            "confetti": ["👻", "👻", "👻", "👻", "👻", "👻", "👻", "👻", "👻", "👻"],
            "decorations": ["👻", "👻"],
            "button_randomize": "👻",
            "button_reset": "👻"
        },
        "fonts": {
            "primary": "Creepster",
            "secondary": "Nosifer",
            "accent": "Eater"
        }
    },
    "thanksgiving": {
        "name": "Thanksgiving Feast",
        "colors": {
            "background": "#422200",
            "text": "#fef3c7",
            "primary": "#f97316",
            "secondary": "#ea580c",
            "accent": "#dc2626",
            "tile_bg": "#5a3010",
            "tile_border": "#f97316",
            "tile_revealed_text": "#fffbeb",
            "neon_glow": "rgba(249, 115, 22, 0.7)",
            "grid": "rgba(220, 38, 38, 0.3)"
        },
        "messages": {
            "bingo": "BINGO!",
            "double_bingo": "DOUBLE BINGO!",
            "h_bingo": "H BINGO!",
            "super_bingo": "You are a God Gamer"
        },
        "emojis": {
            "confetti": ["🦃", "🍂", "🍁", "🌽", "🥧", "🎃", "🍞", "🥔", "🥕", "🌾"],
            "decorations": ["🦃", "🍂"],
            "button_randomize": "🎲",
            "button_reset": "🔄"
        },
        "fonts": {
            "primary": "Amatic SC",
            "secondary": "Patrick Hand",
            "accent": "Satisfy"
        }
    },
    "christmas": {
        "name": "Christmas Wonderland",
        "colors": {
            "background": "#0a3d1a",
            "text": "#fef3c7",
            "primary": "#dc2626",
            "secondary": "#16a34a",
            "accent": "#fbbf24",
            "tile_bg": "#165c33",
            "tile_border": "#dc2626",
            "tile_revealed_text": "#ffffff",
            "neon_glow": "rgba(220, 38, 38, 0.7)",
            "grid": "rgba(251, 191, 36, 0.3)"
        },
        "messages": {
            "bingo": "BINGO!",
            "double_bingo": "DOUBLE BINGO!",
            "h_bingo": "H BINGO!",
            "super_bingo": "You are a God Gamer"
        },
        "emojis": {
            "confetti": ["🎄", "🎅", "⛄", "🎁", "❄️", "⭐", "🔔", "🦌", "🧦", "🍪"],
            "decorations": ["🎄", "⭐"],
            "button_randomize": "🎲",
            "button_reset": "🔄"
        },
        "fonts": {
            "primary": "Mountains of Christmas",
            "secondary": "Fredoka One",
            "accent": "Lobster"
        }
    }
}

def get_theme(theme_name):
    """Get theme configuration by name."""
    return THEMES.get(theme_name, THEMES["alien"])

def list_themes():
    """List all available theme names."""
    return list(THEMES.keys())