import click

from .main import run_with_gui, run_print


@click.option(u'--no_gui', is_flag=True)
@click.command()
def cli(no_gui):
    if no_gui:
        run_print()
    else:
        run_with_gui()


if __name__ == '__main__':
    cli()
