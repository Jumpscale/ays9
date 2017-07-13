from js9 import j
import asyncio

class RecurringTask:
    """Execute a job periodicly"""
    def __init__(self, service, action, period, loop=None):
        self.logger = j.logger.get('j.atyourservice.server')
        self._loop = loop or asyncio.get_event_loop()
        self._future = None
        self._job = None
        self.service = service
        self.action = action
        self.period = period
        self.started = False

    async def _run(self):
        try:
            while self.started:
                # create job
                self._job = self.service.getJob(actionName=self.action)

                # compute how long we need to sleep before next execution
                action_info = self.service.model.actions[self.action]
                elapsed = (j.data.time.epoch - action_info.lastRun)
                sleep = action_info.period - elapsed
                if sleep < 0:
                    sleep = 0

                # wait for right time
                await asyncio.sleep(sleep)

                # execute
                await self._job.execute()

                # update last exection time
                action_info.lastRun = j.data.time.epoch

        except asyncio.CancelledError:
            self.logger.info("recurring task for {}:{} is cancelled".format(self.service, self.action))
            if self._job:
                self._job.cancel()
            raise

    def start(self):
        self.started = True
        self._future = asyncio.ensure_future(self._run(), loop=self._loop)
        return self._future

    def stop(self):
        self.started = False
        # cancel recurring task
        if self._future:
            self._loop.call_soon_threadsafe(self._future.cancel)


class LongRunningTask(RecurringTask):
    def __init__(self, service, action, loop=None):
        super().__init__(service=service, action=action, period=None, loop=loop)
        self.logger.info("Created long task {} of service {}".format(action, service))

    async def _run(self):
        try:
            # create job
            self._job = self.service.getJob(actionName=self.action)
            # execute
            await self._job.execute()
            # update last exection time
        except asyncio.CancelledError:
            self.logger.info("LongRunningTask for {}:{} is cancelled".format(self.service, self.action))
            if self._job:
                self._job.cancel()
            raise


if __name__ == '__main__':
    import logging
    logging.basicConfig()

    loop = asyncio.get_event_loop()

    j.atyourservice.server.aysRepos._load()
    repo = j.atyourservice.server.aysRepos.get('/opt/code/cockpit_repos/testrepo')
    s = repo.serviceGet('node','demo')
    t = RecurringTask(s,'monitor', 10, loop=loop)
    t.start()
    def cb(t):
        t.stop()
    loop.call_later(20, cb, t)
    loop.run_forever()

    from IPython import embed;embed()
