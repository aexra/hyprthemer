"""CLI entry point for hyprthemer."""

import click

from .config import (
    load_config,
    config_exists,
    get_default_config,
    CONFIG_PATH,
    ConfigError
)
from .state import load_state
from .theme import apply_theme
from .monitors import get_monitors, HyprctlError


@click.group()
def cli():
    """Hyprthemer - Theme manager for Hyprland."""
    pass


@cli.command('list')
def list_themes():
    """List available themes."""
    try:
        config = load_config()
    except ConfigError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    click.echo("Available themes:")
    for theme in config.themes:
        click.echo(f"  {theme.name}")
        click.echo(f"    wallpaper: {theme.wallpaper}")
        if theme.post_hooks:
            click.echo(f"    hooks: {len(theme.post_hooks)}")


@cli.command()
@click.argument('theme_name')
@click.option('--monitor', '-m', help='Apply to specific monitor')
@click.option('--all', 'all_monitors', is_flag=True, help='Apply to all monitors')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def apply(theme_name: str, monitor: str, all_monitors: bool, verbose: bool):
    """Apply a theme to monitor(s)."""
    if not monitor and not all_monitors:
        click.echo("Error: Must specify --monitor or --all", err=True)
        raise SystemExit(1)
    
    if monitor and all_monitors:
        click.echo("Error: Cannot use both --monitor and --all", err=True)
        raise SystemExit(1)
    
    try:
        config = load_config()
    except ConfigError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    try:
        result = apply_theme(
            config=config,
            theme_name=theme_name,
            monitor=monitor,
            all_monitors=all_monitors,
            verbose=verbose
        )
    except HyprctlError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    if not result.success:
        if result.error:
            click.echo(f"Error: {result.error}", err=True)
        else:
            click.echo("Some hooks failed:", err=True)
            for hook, success, error in result.hook_results:
                if not success:
                    click.echo(f"  {hook}: {error}", err=True)
        raise SystemExit(1)
    
    monitors_str = ', '.join(result.monitors)
    click.echo(f"Applied theme '{theme_name}' to: {monitors_str}")
    
    if verbose:
        click.echo(f"Executed {len(result.hook_results)} hooks")


@cli.command()
def current():
    """Show current theme state."""
    try:
        config = load_config()
    except ConfigError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    state = load_state(config.state_path)
    
    if state.current_theme:
        click.echo(f"Current theme: {state.current_theme}")
    else:
        click.echo("No theme currently applied")
    
    if state.monitors:
        click.echo("\nMonitor states:")
        for monitor_name, monitor_state in state.monitors.items():
            click.echo(f"  {monitor_name}:")
            click.echo(f"    theme: {monitor_state.theme}")
            click.echo(f"    wallpaper: {monitor_state.wallpaper}")
    else:
        click.echo("\nNo monitor states saved")


@cli.command()
def monitors():
    """List available monitors."""
    try:
        mons = get_monitors()
    except HyprctlError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    click.echo("Available monitors:")
    for mon in mons:
        focused = " (focused)" if mon.focused else ""
        click.echo(f"  {mon.name}{focused}")
        click.echo(f"    {mon.width}x{mon.height}")
        if mon.description:
            click.echo(f"    {mon.description}")


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Overwrite existing config')
def init(force: bool):
    """Create default configuration file."""
    if config_exists() and not force:
        click.echo(f"Config already exists: {CONFIG_PATH}")
        click.echo("Use --force to overwrite")
        raise SystemExit(1)
    
    # Ensure directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_PATH, 'w') as f:
        f.write(get_default_config())
    
    click.echo(f"Created config: {CONFIG_PATH}")
    click.echo("Edit the file to add your themes")


if __name__ == "__main__":
    cli()
