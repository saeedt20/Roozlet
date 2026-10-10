"""Application-private Fontconfig registration; no system configuration writes."""

import ctypes
import ctypes.util

from .resources import DATA


def load():
    warnings = []
    try:
        fc = ctypes.CDLL(ctypes.util.find_library("fontconfig"))
        fc.FcConfigGetCurrent.restype = ctypes.c_void_p
        fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fc.FcConfigAppFontAddFile.restype = ctypes.c_int
        config = fc.FcConfigGetCurrent()
        paths = list((DATA / "fonts/vazirmatn").glob("*.ttf"))
        if not paths:
            warnings.append("No bundled font files were found")
        for path in paths:
            if not fc.FcConfigAppFontAddFile(config, str(path).encode()):
                warnings.append(path.name)
        from gi.repository import PangoCairo

        PangoCairo.FontMap.get_default().changed()
    except (OSError, AttributeError, TypeError) as e:
        warnings.append(str(e))
    return warnings


def family(cfg):
    from gi.repository import PangoCairo

    mode = cfg["appearance"]["font_mode"]
    chosen = (
        "Vazirmatn"
        if mode == "vazirmatn"
        else cfg["appearance"]["custom_font_family"]
        if mode == "custom"
        else "Sans"
    )
    names = {f.get_name().casefold() for f in PangoCairo.FontMap.get_default().list_families()}
    return chosen if chosen.casefold() in names or chosen == "Sans" else "Sans"
