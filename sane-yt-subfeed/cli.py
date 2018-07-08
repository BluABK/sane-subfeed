import click

from .main import run_with_gui, run_print


@click.option(u'--tui', is_flag=True)
@click.command()
def cli(tui):
    if tui:
        run_print()
    else:
        run_with_gui()


if __name__ == '__main__':
    cli()
