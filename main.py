#!/usr/bin/python3

# Click library has some problems with python3 when it comes to unicode: http://click.pocoo.org/5/python3/#python3-surrogates
# to fix this we need to set the environ variables to export the locales

from js9 import j
j.tools.prefab.local.bash.locale_check()

import click
import logging

from JumpScale9AYS.ays.server.app import app as sanic_app

sanic_app.config['REQUEST_TIMEOUT'] = 3600


def configure_logger(level):
    if level == 'DEBUG':
        click.echo("debug logging enabled")
    # configure jumpscale loggers
    j.logger.loggers_level_set(level)
    # configure asyncio logger
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.handlers = []
    asyncio_logger.addHandler(j.logger.handlers.consoleHandler)
    asyncio_logger.addHandler(j.logger.handlers.fileRotateHandler)
    asyncio_logger.setLevel(level)


@click.command()
@click.option('--host', '-h', default='127.0.0.1', help='listening address')
@click.option('--port', '-p', default=5000, help='listening port')
@click.option('--log', '-l', default='info', help='set logging level (error, warning, info, debug)')
@click.option('--dev', default=False, is_flag=True, help='enable development mode')
def main(host, port, log, dev):
    if not j.core.db:
        j.clients.redis.start4core()
    log = log.upper()
    if log not in ('ERROR', 'WARNING', 'INFO', 'DEBUG'):
        click.echo("logging level not valid", err=True)
        return

    configure_logger(log)
    debug = log == 'DEBUG'

    # load the app
    @sanic_app.listener('before_server_start')
    async def init_ays(sanic, loop):
        loop.set_debug(debug)
        j.atyourservice.server.debug = debug
        j.atyourservice.server.dev_mode = dev
        if j.atyourservice.server.dev_mode:
            j.atyourservice.server.logger.info("development mode enabled")

        if not dev:
            # Generate/Load ays_repos ssh key which will be used to auto push repos changes
            local_prefab = j.tools.prefab.local
            key_path = local_prefab.system.ssh.keygen(name='ays_repos_key').split(".pub")[0]
            key = j.clients.sshkey.get('ays_repo_key', data={'path': key_path}, interactive=False)
            key.load()

        j.atyourservice.server._start(loop=loop)

    @sanic_app.listener('after_start')
    async def after_start(sanic, loop):
        print("AYS server running at http://{}:{}".format(host, port))

    @sanic_app.listener('after_stop')
    async def stop_ays(sanic, loop):
        await j.atyourservice.server._stop()

    # start server
    sanic_app.run(debug=debug, host=host, port=port, workers=1)


if __name__ == '__main__':
    main()
