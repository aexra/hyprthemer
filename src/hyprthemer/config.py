"""Configuration loading and validation for hyprthemer."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


CONFIG_PATH = Path.home() / ".config" / "hypr" / "hyprthemer.toml"
DEFAULT_STATE_PATH = Path.home() / ".cache" / "hyprthemer" / "state.toml"


@dataclass
class ThemeConfig:
    """Theme configuration from config file."""
    name: str
    wallpaper: str
    post_hooks: List[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration."""
    state_path: Path
    default_post_hooks: List[str]
    themes: List[ThemeConfig]

    def get_theme(self, name: str) -> Optional[ThemeConfig]:
        """Get theme by name."""
        return next((t for t in self.themes if t.name == name), None)

    def get_theme_names(self) -> List[str]:
        """Get list of all theme names."""
        return [t.name for t in self.themes]


class ConfigError(Exception):
    """Configuration error."""
    pass


def expand_path(path_str: str) -> Path:
    """Expand ~ and environment variables in path."""
    return Path(path_str).expanduser()


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from TOML file."""
    path = config_path or CONFIG_PATH
    
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    
    try:
        with open(path, 'rb') as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in config: {e}")
    
    # Parse settings
    settings = data.get('settings', {})
    state_path = expand_path(settings.get('state_path', str(DEFAULT_STATE_PATH)))
    
    # Parse defaults
    defaults = data.get('defaults', {})
    default_post_hooks = defaults.get('post_hooks', [])
    
    # Parse themes
    themes_data = data.get('themes', [])
    if not themes_data:
        raise ConfigError("No themes defined in config")
    
    themes = []
    for theme_data in themes_data:
        if 'name' not in theme_data:
            raise ConfigError("Theme missing required 'name' field")
        if 'wallpaper' not in theme_data:
            raise ConfigError(f"Theme '{theme_data['name']}' missing required 'wallpaper' field")
        
        wallpaper_path = expand_path(theme_data['wallpaper'])
        if not wallpaper_path.exists():
            raise ConfigError(f"Wallpaper not found: {wallpaper_path}")
        
        themes.append(ThemeConfig(
            name=theme_data['name'],
            wallpaper=str(wallpaper_path),
            post_hooks=theme_data.get('post_hooks', [])
        ))
    
    return Config(
        state_path=state_path,
        default_post_hooks=default_post_hooks,
        themes=themes
    )


def config_exists(config_path: Optional[Path] = None) -> bool:
    """Check if config file exists."""
    path = config_path or CONFIG_PATH
    return path.exists()


def get_default_config() -> str:
    """Return default configuration template."""
    return '''[settings]
state_path = "~/.cache/hyprthemer/state.toml"

# Default hooks executed for all themes
[defaults]
post_hooks = [
    "swww img $HYPRTHEMER_WALLPAPER --transition-type fade",
    # "wal -i $HYPRTHEMER_WALLPAPER -n"
]

# Define your themes below
[[themes]]
name = "example-theme"
wallpaper = "~/wallpapers/example.jpg"
# Theme-specific hooks (run after default hooks)
post_hooks = [
    "notify-send 'Theme applied: example-theme'"
]
'''

