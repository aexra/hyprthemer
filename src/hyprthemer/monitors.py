"""Monitor detection via hyprctl."""

import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Monitor:
    """Hyprland monitor information."""
    name: str
    description: str
    width: int
    height: int
    focused: bool


class HyprctlError(Exception):
    """Error communicating with hyprctl."""
    pass


def get_monitors() -> List[Monitor]:
    """Get list of monitors from hyprctl."""
    try:
        result = subprocess.run(
            ['hyprctl', 'monitors', '-j'],
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        raise HyprctlError("hyprctl not found. Is Hyprland running?")
    except subprocess.CalledProcessError as e:
        raise HyprctlError(f"hyprctl failed: {e.stderr}")
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HyprctlError("Invalid JSON from hyprctl")
    
    monitors = []
    for mon in data:
        monitors.append(Monitor(
            name=mon.get('name', 'unknown'),
            description=mon.get('description', ''),
            width=mon.get('width', 0),
            height=mon.get('height', 0),
            focused=mon.get('focused', False)
        ))
    
    return monitors


def get_monitor_names() -> List[str]:
    """Get list of monitor names."""
    return [m.name for m in get_monitors()]


def get_focused_monitor() -> Optional[Monitor]:
    """Get currently focused monitor."""
    monitors = get_monitors()
    return next((m for m in monitors if m.focused), None)


def validate_monitor(monitor_name: str) -> bool:
    """Check if monitor name is valid."""
    return monitor_name in get_monitor_names()

