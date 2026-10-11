from ..fonts import family

THEMES = {
    "dark": {"bg": "#14252E", "fg": "#F0F5F7", "muted": "#B8C5CC", "line": "#314550", "holiday": "#FF9B92"},
    "light": {"bg": "#F4F6F5", "fg": "#172C35", "muted": "#48606B", "line": "#CDD8D7", "holiday": "#A23330"},
}


def rgb(s):
    return tuple(int(s[i : i + 2], 16) / 255 for i in (1, 3, 5))


def luminance(s):
    v = rgb(s)
    v = [n / 12.92 if n <= 0.04045 else ((n + 0.055) / 1.055) ** 2.4 for n in v]
    return sum(a * b for a, b in zip(v, (0.2126, 0.7152, 0.0722)))


def foreground(accent):
    return "#000000" if luminance(accent) > 0.179 else "#FFFFFF"


def tokens(cfg, today=None, viewed_month=None, season=None):
    t = dict(THEMES[cfg["appearance"]["theme"]])
    from ..calendar_service import civil_day
    from ..seasons import ACCENTS, effective_season

    today = today or civil_day(cfg["timezone"])
    t["season"] = season or effective_season(cfg, today, viewed_month)
    a = cfg["appearance"]
    t["seasonal"] = a.get("style") == "seasonal"
    if t["seasonal"]:
        t["bg"] = "#171D27" if a["theme"] == "dark" else "#F6F4F0"
    t["accent"] = (ACCENTS[a["theme"]][t["season"]]
                   if t["seasonal"] and a.get("accent_source") == "seasonal"
                   else a["accent_color"])
    t["selected_fg"] = foreground(t["accent"])
    # Keep text accents readable while preserving the user's original selection fill.
    v = list(rgb(t["accent"]))
    bg = luminance(t["bg"])
    for _ in range(40):
        color = "#" + "".join(f"{round(c * 255):02X}" for c in v)
        lum = luminance(color)
        if (max(lum, bg) + 0.05) / (min(lum, bg) + 0.05) >= 4.5:
            break
        v = [c * 0.85 for c in v] if bg > 0.5 else [c + (1 - c) * 0.15 for c in v]
    t["accent_text"] = color
    return t


def apply(cfg, provider, today=None):
    t = tokens(cfg, today)
    f = family(cfg).replace('"', "")
    size = 11 * cfg["appearance"]["text_scale"]
    css = f'''
 .rooz {{ background-color: {t["bg"]}; color: {t["fg"]}; font-family: "{f}"; font-size: {size}px; }}
 .rooz label {{ color: {t["fg"]}; }}
 .rooz .muted {{ color: {t["muted"]}; }}
 .rooz .heading {{ font-size: {size * 1.7}px; font-weight: 600; }}
 .rooz button {{ background-image: none; background-color: transparent; border: 1px solid transparent; border-radius: 9px; box-shadow: none; color: {t["fg"]}; padding: 5px 9px; }}
 .rooz button:hover {{ background-color: alpha({t["accent"]},0.12); }}
 .rooz button:focus {{ border-color: {t["accent_text"]}; }}
 .rooz button.day {{ padding: 1px; min-width: 30px; min-height: 32px; }}
 .rooz button.day .primary {{ font-size: {size * 1.75}px; font-weight: 500; }}
 .rooz button.selected {{ background-color: {t["accent"]}; }}
 .rooz button.selected label {{ color: {t["selected_fg"]}; }}
 .rooz button.today {{ border: 2px solid {t["accent_text"]}; }}
 .rooz button.today.selected {{ box-shadow: inset 0 0 0 2px {t["bg"]}; }}
 .rooz .holiday {{ color: {t["holiday"]}; }}
 .rooz .friday {{ color: {t["holiday"]}; }}
 .rooz separator {{ background: {t["line"]}; min-height: 1px; }}
 .rooz entry, .rooz spinbutton, .rooz combobox button {{ background-color: alpha({t["muted"]},0.08); color: {t["fg"]}; border: 1px solid {t["line"]}; }}
 .rooz notebook stack {{ background-color: {t["bg"]}; }}
 .rooz notebook header {{ background: alpha({t["muted"]},0.05); }}
 .rooz notebook tab {{ background: transparent; color: {t["fg"]}; }}
 .rooz notebook tab:checked {{ background: {t["bg"]}; color: {t["fg"]}; border-bottom: 2px solid {t["accent_text"]}; }}
 .rooz scale highlight, .rooz switch:checked {{ background-color: {t["accent"]}; }}
 window.rooz-card {{ background: transparent; }}
 .rooz-card button {{ background: transparent; border: none; box-shadow: none; padding: 0; min-width: 24px; min-height: 24px; }}
 '''
    from ..seasons import SEASONS
    # One bounded provider contains four scoped variants. A browsed season never
    # changes another window's colors or accumulates providers on navigation.
    variants = []
    for season in SEASONS:
        st = tokens(cfg, today, season=season)
        variant = css
        for key in ("bg", "fg", "muted", "line", "holiday", "accent", "accent_text", "selected_fg"):
            variant = variant.replace(t[key], "__" + key + "__")
        for key in ("bg", "fg", "muted", "line", "holiday", "accent", "accent_text", "selected_fg"):
            variant = variant.replace("__" + key + "__", st[key])
        variant = variant.replace(".rooz ", ".rooz.season-" + season + " ")
        variant = variant.replace(".rooz {", ".rooz.season-" + season + " {")
        variants.append(variant)
    css += "\n" + "\n".join(variants)
    css += """
    .rooz button.day { border: 1px solid alpha(currentColor,0.10); border-radius: 8px; }
    .rooz .sidebar { padding: 12px; background: alpha(currentColor,0.025); }
    .rooz .sidebar button { padding: 10px 8px; font-size: 12px; }
    .rooz button.month-title { font-size: 20px; font-weight: 600; }
    .rooz .details-panel { padding: 14px; border-radius: 14px; }
    .rooz-card button.occasion { font-size: 10.5px; padding: 0; }
    """
    for season in SEASONS:
        st = tokens(cfg, today, season=season)
        css += f"\n.rooz.season-{season} button.day.today {{ border: 2px solid {st['accent_text']}; }}"
    provider.load_from_data(css.encode())


def style_window(widget, cfg, today, viewed_month=None):
    from ..seasons import SEASONS, effective_season
    context = widget.get_style_context()
    for season in SEASONS:
        context.remove_class("season-" + season)
    season = effective_season(cfg, today, viewed_month)
    context.add_class("season-" + season)
    return season
