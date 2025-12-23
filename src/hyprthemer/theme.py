"""Theme application logic for hyprthemer."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import Config, ThemeConfig, CONFIG_PATH
from .state import State, load_state, save_state, update_monitor_state, update_all_monitors_state
from .hooks import execute_hooks
from .monitors import get_monitor_names, validate_monitor


@dataclass
class ApplyResult:
    """Result of applying a theme."""
    success: bool
    theme_name: str
    monitors: List[str]
    hook_results: List[tuple[str, bool, Optional[str]]]
    error: Optional[str] = None


def apply_theme(
    config: Config,
    theme_name: str,
    monitor: Optional[str] = None,
    all_monitors: bool = False,
    verbose: bool = False
) -> ApplyResult:
    """
    Apply a theme to specified monitor(s).
    
    Args:
        config: Loaded configuration
        theme_name: Name of theme to apply
        monitor: Specific monitor name (mutually exclusive with all_monitors)
        all_monitors: Apply to all monitors
        verbose: Print verbose output
    
    Returns:
        ApplyResult with success status and hook results
    """
    # Validate theme exists
    theme = config.get_theme(theme_name)
    if not theme:
        return ApplyResult(
            success=False,
            theme_name=theme_name,
            monitors=[],
            hook_results=[],
            error=f"Theme '{theme_name}' not found"
        )
    
    # Determine target monitors
    if all_monitors:
        target_monitors = get_monitor_names()
        monitor_env = "all"
    elif monitor:
        if not validate_monitor(monitor):
            return ApplyResult(
                success=False,
                theme_name=theme_name,
                monitors=[],
                hook_results=[],
                error=f"Monitor '{monitor}' not found"
            )
        target_monitors = [monitor]
        monitor_env = monitor
    else:
        return ApplyResult(
            success=False,
            theme_name=theme_name,
            monitors=[],
            hook_results=[],
            error="Must specify --monitor or --all"
        )
    
    # Load and update state
    state = load_state(config.state_path)
    
    if all_monitors:
        state = update_all_monitors_state(
            state,
            target_monitors,
            theme_name,
            theme.wallpaper
        )
    else:
        state = update_monitor_state(
            state,
            monitor,
            theme_name,
            theme.wallpaper
        )
    
    # Save state before running hooks
    save_state(state, config.state_path)
    
    # Collect hooks: defaults + theme-specific
    all_hooks = config.default_post_hooks + theme.post_hooks
    
    # Execute hooks
    hook_results = execute_hooks(
        hooks=all_hooks,
        theme_name=theme_name,
        wallpaper=theme.wallpaper,
        monitor=monitor_env,
        config_path=CONFIG_PATH,
        state_path=config.state_path,
        verbose=verbose
    )
    
    # Check if any hooks failed
    hooks_success = all(success for _, success, _ in hook_results)
    
    return ApplyResult(
        success=hooks_success,
        theme_name=theme_name,
        monitors=target_monitors,
        hook_results=hook_results
    )

