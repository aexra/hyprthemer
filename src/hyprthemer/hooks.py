"""Post-hooks execution for hyprthemer."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional


def build_hook_env(
    theme_name: str,
    wallpaper: str,
    monitor: str,
    config_path: Path,
    state_path: Path
) -> dict:
    """Build environment variables for hook execution."""
    env = os.environ.copy()
    env.update({
        'HYPRTHEMER_THEME': theme_name,
        'HYPRTHEMER_WALLPAPER': wallpaper,
        'HYPRTHEMER_MONITOR': monitor,
        'HYPRTHEMER_CONFIG': str(config_path),
        'HYPRTHEMER_STATE': str(state_path),
    })
    return env


def execute_hook(
    hook: str,
    env: dict,
    verbose: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Execute a single hook command.
    
    Returns (success, error_message).
    """
    try:
        result = subprocess.run(
            hook,
            shell=True,
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, result.stderr or f"Hook exited with code {result.returncode}"
        return True, None
    except Exception as e:
        return False, str(e)


def execute_hooks(
    hooks: List[str],
    theme_name: str,
    wallpaper: str,
    monitor: str,
    config_path: Path,
    state_path: Path,
    verbose: bool = False
) -> List[tuple[str, bool, Optional[str]]]:
    """
    Execute list of hooks with environment variables.
    
    Returns list of (hook, success, error_message) tuples.
    """
    env = build_hook_env(
        theme_name=theme_name,
        wallpaper=wallpaper,
        monitor=monitor,
        config_path=config_path,
        state_path=state_path
    )
    
    results = []
    for hook in hooks:
        success, error = execute_hook(hook, env, verbose)
        results.append((hook, success, error))
    
    return results

