"""State management for hyprthemer."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import tomli_w


@dataclass
class MonitorState:
    """State for a single monitor."""
    wallpaper: str
    theme: str


@dataclass
class State:
    """Current hyprthemer state."""
    current_theme: Optional[str] = None
    monitors: Dict[str, MonitorState] = field(default_factory=dict)


def load_state(state_path: Path) -> State:
    """Load state from TOML file."""
    if not state_path.exists():
        return State()
    
    try:
        with open(state_path, 'rb') as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError:
        # Corrupted state, return empty
        return State()
    
    # Parse global section
    global_data = data.get('global', {})
    current_theme = global_data.get('current_theme')
    
    # Parse monitors section
    monitors_data = data.get('monitors', {})
    monitors = {}
    for monitor_name, monitor_info in monitors_data.items():
        if 'wallpaper' in monitor_info and 'theme' in monitor_info:
            monitors[monitor_name] = MonitorState(
                wallpaper=monitor_info['wallpaper'],
                theme=monitor_info['theme']
            )
    
    return State(
        current_theme=current_theme,
        monitors=monitors
    )


def save_state(state: State, state_path: Path) -> None:
    """Save state to TOML file."""
    # Ensure parent directory exists
    state_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build state dictionary
    data = {}
    
    # Global section
    if state.current_theme:
        data['global'] = {'current_theme': state.current_theme}
    
    # Monitors section
    if state.monitors:
        data['monitors'] = {
            name: {
                'wallpaper': ms.wallpaper,
                'theme': ms.theme
            }
            for name, ms in state.monitors.items()
        }
    
    with open(state_path, 'wb') as f:
        tomli_w.dump(data, f)


def update_monitor_state(
    state: State,
    monitor: str,
    theme_name: str,
    wallpaper: str
) -> State:
    """Update state for a specific monitor."""
    state.monitors[monitor] = MonitorState(
        wallpaper=wallpaper,
        theme=theme_name
    )
    state.current_theme = theme_name
    return state


def update_all_monitors_state(
    state: State,
    monitors: list,
    theme_name: str,
    wallpaper: str
) -> State:
    """Update state for all monitors."""
    for monitor in monitors:
        state.monitors[monitor] = MonitorState(
            wallpaper=wallpaper,
            theme=theme_name
        )
    state.current_theme = theme_name
    return state

