"""
ci

Easily run common CI tasks for Python builds.
"""

import platform
import subprocess

import click


__title__ = 'ci'
__version__ = '0.1.1'
__url__ = 'https://github.com/rossmacarthur/python-ci'
__author__ = 'Ross MacArthur'
__author_email__ = 'ross@macarthur.io'
__license__ = 'MIT'
__description__ = 'Easily run common CI tasks for Python builds.'


def info(message):
    """
    Pretty print a message.
    """
    click.secho('ci: ', bold=True, fg='cyan', nl=False)
    click.secho(message, bold=True, fg='white')


@click.command(
    context_settings={
        'ignore_unknown_options': True
    }
)
@click.version_option(
    None,
    '--version',
    prog_name='ci',
    message='%(prog)s %(version)s'
)
@click.option(
    '--only',
    help='Only run the given command if we are using the specified version.'
)
@click.option(
    '--skip',
    help='Skip running the given command if we are NOT using the specified version.'
)
@click.option(
    '--shell',
    is_flag=True,
    help='Run the subcommand in a shell.'
)
@click.argument('command', nargs=-1)
@click.pass_context
def cli(ctx, only, skip, shell, command):
    """
    Easily run common CI tasks in Python

    Example usage:

    \b
        ci --skip 2.7 flake8             # run `flake8` on Python 2.7 only
        ci --only 3 pip install codecov  # run `pip install codecov` on Python 3.x.x only
        ci --only 3.7.2 codecov          # run `codecov` on Python 3.7.2 only

    If for some reason you are running a command that takes the same options
    as this tool then you can use two dashes `--` to specify that this tool
    should no longer match options.

    Example:

    \b
        ci --only 3 -- python --version
    """
    if only and skip:
        raise click.UsageError('--only and --skip are mutually exclusive')

    version = platform.python_version()

    if (
        (not only and not skip)
        or (only and version.startswith(only))
        or (skip and not version.startswith(skip))
    ):
        info(' '.join(command))
        returncode = subprocess.call(command, shell=shell)
        info('exiting with {}'.format(returncode))
        ctx.exit(returncode)
