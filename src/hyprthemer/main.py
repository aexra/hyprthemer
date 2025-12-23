import click

@click.group()
def cli():
    """Hyprthemer."""
    pass

@cli.command()
@click.argument('name')
def hello(name):
    """Greets the user."""
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    cli()
