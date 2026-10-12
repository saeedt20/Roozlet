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
    from ..seasons import SEASONS
    from .motion import enabled
    font = family(cfg).replace('"', "")
    size = 13 * cfg["appearance"]["text_scale"]
    duration = "140ms" if enabled(cfg) else "0s"

    def rules(t):
        panel = "#1D2530" if cfg["appearance"]["theme"] == "dark" else "#EEEBE5"
        return f'''
        .rooz {{ background-color:{t["bg"]}; color:{t["fg"]}; font-family:"{font}"; font-size:{size}px; }}
        .rooz label {{ color:{t["fg"]}; }}
        .rooz .muted {{ color:{t["muted"]}; font-size:{size*.90}px; }}
        .rooz .heading {{ font-size:{size*1.55}px; font-weight:600; }}
        .rooz headerbar {{ background:{panel}; background-image:none; color:{t["fg"]}; border-bottom:1px solid {t["line"]}; box-shadow:none; padding:6px 10px; }}
        .rooz headerbar .title {{ color:{t["fg"]}; font-size:{size}px; }}
        .rooz decoration {{ border:1px solid {t["line"]}; box-shadow:none; margin:0; }}
        .rooz button {{ background-image:none; background-color:transparent; border:1px solid transparent; border-radius:9px; box-shadow:none; color:{t["fg"]}; padding:6px 10px; transition:background-color {duration} ease-out,border-color {duration} ease-out,color {duration} ease-out; }}
        .rooz button label {{ color:{t["fg"]}; }}
        .rooz button:hover {{ background-color:alpha({t["accent"]},.12); }}
        .rooz button:active {{ background-color:alpha({t["accent"]},.20); }}
        .rooz button:focus {{ border-color:{t["accent_text"]}; }}
        .rooz button.selected {{ background-color:{t["accent"]}; }}
        .rooz button.selected label {{ color:{t["selected_fg"]}; }}
        .rooz button.day {{ padding:2px; min-width:30px; min-height:36px; border-radius:9px; }}
        .rooz button.day .primary {{ font-size:{size*1.65}px; font-weight:500; }}
        .rooz button.day .muted {{ font-size:{size*.85}px; }}
        .rooz button.today {{ border:2px solid {t["accent_text"]}; }}
        .rooz button.today.selected {{ box-shadow:inset 0 0 0 2px {t["bg"]}; }}
        .rooz .holiday, .rooz .friday {{ color:{t["holiday"]}; }}
        .rooz .sidebar {{ padding:12px; background:{panel}; }}
        .rooz .brand-mark {{ color:{t["accent_text"]}; }}
        .rooz .sidebar button {{ padding:10px 8px; font-size:{size}px; }}
        .rooz .sidebar button.selected {{ background-color:alpha({t["accent"]},.17); color:{t["accent_text"]}; }}
        .rooz .sidebar button.selected label {{ color:{t["accent_text"]}; }}
        .rooz .hero {{ background:{panel}; border-radius:12px; }}
        .rooz .hero.scenic label {{ color:#F4F6F8; }}
        .rooz .hero.scenic .muted {{ color:#DEE5EE; }}
        .rooz .hero.scenic button {{ background-color:alpha(#101A28,.72); color:#F4F6F8; border:1px solid alpha(#F4F6F8,.20); }}
        .rooz .hero.scenic button label {{ color:#F4F6F8; }}
        .rooz .hero button.month-title {{ background:transparent; border-color:transparent; font-size:{size*1.6}px; font-weight:600; padding:0; }}
        .rooz .hero button.month-title:focus {{ border-color:{t["accent_text"]}; }}
        .rooz .hero.scenic button:hover {{ background-color:alpha(#101A28,.90); }}
        .rooz .preferences-group,.rooz .details-panel {{ background:{panel}; border:1px solid {t["line"]}; border-radius:12px; }}
        .rooz .preference-row {{ padding:12px; }}
        .rooz .details-panel {{ padding:14px; }}
        .rooz button.search-result {{ background:{panel}; border:1px solid {t["line"]}; padding:12px; }}
        .rooz .detail-heading {{ font-size:{size*1.10}px; font-weight:600; }}
        .rooz button.copy-button {{ border:1px solid {t["line"]}; background-color:alpha({t["muted"]},.05); }}
        .rooz .preview-date {{ background-color:alpha({t["bg"]},.88); border:1px solid alpha({t["muted"]},.18); border-radius:10px; padding:8px; }}
        .rooz .preview-primary {{ background-color:{t["accent"]}; border-radius:10px; padding:8px; }}
        .rooz .hero .preview-primary label, .rooz .hero.scenic .preview-primary label, .rooz .hero .preview-primary .muted {{ color:{t["selected_fg"]}; }}
        .rooz .preview-number {{ font-size:{size*2.15}px; font-weight:600; }}
        .rooz .hero.scenic .preview-date {{ background-color:alpha(#17202E,.90); }}
        .rooz .season-tile {{ padding:3px; border:1px solid {t["line"]}; }}
        .rooz .season-choice {{ border:2px solid {t["accent_text"]}; background:alpha({t["accent"]},.08); }}
        .rooz .season-choice label {{ color:{t["accent_text"]}; }}
        .rooz flowboxchild {{ padding:0; background:transparent; }}
        .rooz separator {{ background:{t["line"]}; min-height:1px; }}
        .rooz .preferences-group separator {{ margin:0 12px; }}
        .rooz entry,.rooz spinbutton,.rooz combobox button {{ background-color:alpha({t["muted"]},.08); color:{t["fg"]}; border:1px solid {t["line"]}; }}
        .rooz switch {{ background:{t["line"]}; border:1px solid {t["line"]}; border-radius:20px; color:{t["fg"]}; }}
        .rooz switch:checked {{ background:{t["accent"]}; color:{t["selected_fg"]}; border-color:{t["accent"]}; }}
        .rooz switch slider {{ background:{t["fg"]}; background-image:none; border:0; border-radius:20px; box-shadow:none; }}
        .rooz switch:checked slider {{ background:{t["selected_fg"]}; }}
        .rooz scale trough {{ background:{t["line"]}; border:none; min-height:4px; }}
        .rooz scale highlight {{ background:{t["accent"]}; border:none; }}
        .rooz scale slider {{ background:{t["accent"]}; border:none; min-width:12px; min-height:12px; box-shadow:none; }}
        .rooz menu {{ background:{t["bg"]}; color:{t["fg"]}; }}
        .rooz menuitem:hover {{ background:alpha({t["accent"]},.15); }}
        .rooz textview,.rooz textview text {{ background:{panel}; color:{t["fg"]}; }}
        .rooz .about-tabs button {{ padding:6px 8px; min-width:0; }}
        .rooz .about-tabs button:checked {{ background:alpha({t["accent"]},.17); }}
        .rooz .about-tabs button:checked label {{ color:{t["accent_text"]}; }}
        window.rooz-card {{ background:transparent; }}
        .rooz-card button {{ background:transparent; border:none; box-shadow:none; padding:0; min-width:24px; min-height:24px; }}
        .rooz-card button.occasion {{ font-size:10.5px; padding:0; }}
        '''

    css = rules(tokens(cfg, today))
    for season in SEASONS:
        variant = rules(tokens(cfg, today, season=season))
        variant = variant.replace(".rooz ", ".rooz.season-" + season + " ")
        variant = variant.replace(".rooz {", ".rooz.season-" + season + " {")
        css += variant
    css += ".rooz.reduced-motion button, .rooz.reduced-motion switch, .rooz.reduced-motion scale { transition:none; }"
    provider.load_from_data(css.encode())


def style_window(widget, cfg, today, viewed_month=None):
    from ..seasons import SEASONS, effective_season
    context = widget.get_style_context()
    from .motion import enabled
    context.remove_class("reduced-motion") if enabled(cfg, widget) else context.add_class("reduced-motion")
    for season in SEASONS:
        context.remove_class("season-" + season)
    season = effective_season(cfg, today, viewed_month)
    context.add_class("season-" + season)
    return season
