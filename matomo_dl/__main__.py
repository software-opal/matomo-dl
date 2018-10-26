import click

from .distribution.load.file import load_distribution_file


@click.group()
def cli():
    pass


@cli.command()
@click.argument('distribution_file', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
def update(distribution_file):
    distribution_file = pathlib.Path(distribution_file)
    distribution_lock_file = distribution_file.with_suffix(
        '.lock' + distribution_file.suffix)

    dist = load_distribution_file(
        distribution_file.parent, distribution_file.text())


@cli.command()
def build():
    click.echo('Dropped the database')


if __name__ == '__main__':
    cli()
