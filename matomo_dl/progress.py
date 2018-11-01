import click


def progressbar(*a, **k):
    progress = click.progressbar(*a, **k)
    progress.short_limit = 0
    return progress
