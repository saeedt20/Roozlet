from pathlib import Path

from .config import atomic_write, config_home


def path():
    return config_home() / "autostart/rooz.desktop"


def enabled():
    try:
        text = path().read_text()
        return (
            "Exec=/usr/bin/rooz --widget" in text
            and "Hidden=true" not in text
            and "X-GNOME-Autostart-enabled=false" not in text
        )
    except OSError:
        return False


def set_enabled(value, executable="/usr/bin/rooz"):
    if value:
        if not Path(executable).is_file():
            raise ValueError("Install Roozlet before enabling login startup.")
        atomic_write(
            path(),
            "[Desktop Entry]\nType=Application\nName=Roozlet\nName[fa]=روزلت\nExec=/usr/bin/rooz --widget\nTryExec=/usr/bin/rooz\nTerminal=false\nX-GNOME-Autostart-enabled=true\n",
        )
    else:
        path().unlink(missing_ok=True)
