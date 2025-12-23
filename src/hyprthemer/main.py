import click
import subprocess

@click.group()
def cli():
    """Hyprthemer."""
    pass

@cli.command()
def test():
    """Reads and displays the system hostname."""
    try:
        result = subprocess.run(
            ['cat', '/etc/hostname'],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: Command failed with code {e.returncode}", err=True)
    except FileNotFoundError:
        click.echo("Error: Command not found", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
