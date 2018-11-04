import click


# Typed in the .pyi file
def progressbar(*a, **k):
    progress = click.progressbar(*a, **k)
    progress.short_limit = 0  # typing: ignore
    return progress
