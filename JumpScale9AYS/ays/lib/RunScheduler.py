import asyncio
from js9 import j

NORMAL_RUN_PRIORITY = 1
ERROR_RUN_PRIORITY = 10


class RunScheduler:
    """
    This class is reponsible to execte the run requested by the users
    as well as the automatic error runs

    Since only one can be executed at a time, all the run are pushed on a PriorityQueue.
    Requested runs have always hightest priority over error runs.
    """

    def __init__(self, repo):
        self.logger = j.logger.get("j.ays.RunScheduler")
        self.repo = repo
        self.queue = asyncio.PriorityQueue(maxsize=0, loop=self.repo._loop)
        self._retries = []
        self._retries_lock = asyncio.Lock(loop=self.repo._loop)
        self._accept = False
        self._is_running = False
        self._current = None

    def get_run_retries(self, retries):
        """
        sets the retry delays and number
        @param retry_config: list containing the delay values.
        """
        retry_delay = {}
        if retries[0] != 0:
            for idx, value in enumerate(retries):
                if value == '0':
                    raise j.exceptions.Input("Retry delay value can't be 0")
                retry_delay[idx + 1] = value
        return retry_delay

    @property
    def status(self):
        if self._accept and self._is_running:
            return "running"
        if not self._accept and self._is_running:
            return "stopping"
        return "halted"

    @property
    def current_run(self):
        """
        returns the run that is currently beeing executed.
        """
        if self._current is not None:
            try:
                run_model = j.core.jobcontroller.db.runs.get(self._current)
                return run_model.objectGet()
            except j.exceptions.Input:
                return None
        return None

    def _commit(self, run):
        """
        create a commit on the ays repo
        """
        self.logger.debug("Create commit on repo %s for un %s", self.repo.path, run.model.key)
        msg = "Run {}\n\n{}".format(run.model.key, str(run))
        self.repo.commit(message=msg)

    async def start(self):
        """
        starts the run scheduler and begin whating the run queue.
        """
        self.logger.info("{} started".format(self))
        if self._is_running:
            return

        self._is_running = True
        self._accept = True
        while self._is_running:

            try:
                _, run = await asyncio.wait_for(self.queue.get(), timeout=10)
            except asyncio.TimeoutError:
                # this allow to exit the loop when stopped is asked.
                # without the timeout the queue.get blocks forever
                if not self._accept:
                    break
                continue

            try:
                self._current = run.model.key
                await run.execute()
                self._commit(run)
            except:
                # retry the run after a delay, skip if 0 retries are configured.
                if self.get_run_retries(run.retries):
                    await self._retry(run)
            finally:
                self._current = None
                self.queue.task_done()

        self._is_running = False
        self.logger.info("{} stopped".format(self))

    async def stop(self, timeout=30):
        """
        stops the run scheduler
        When the run scheduler is stopped you can't add send new run to it
        @param timout: number of second we wait for the current run to finish before force stopping execution.

        """
        self._accept = False
        self.logger.info("{} stopping...".format(self))

        try:
            # wait for runs in the queue and all retries actions
            with await self._retries_lock:
                for retry in self._retries:
                    retry.cancel()
            to_wait = [self.queue.join(), *self._retries]
            await asyncio.wait(to_wait, timeout=timeout, loop=self.repo._loop)

        except asyncio.TimeoutError:
            self.logger.warning("stop timeout reach for {}. possible run interrupted".format(self))
        except Exception as e:
            self.logger.error("unknown exception during stopping of {}: {}".format(self, e))
            raise
        finally:
            self._retries = []

    async def add(self, run, priority=NORMAL_RUN_PRIORITY):
        """
        add a run to the queue of run to be executed
        @param priority: one of NORMAL_RUN_PRIORITY or ERROR_RUN_PRIORITY
                         runs added with NORMAL_RUN_PRIORITY will always be executed before
                         the ones added with ERROR_RUN_PRIORITY
        """
        if priority not in [NORMAL_RUN_PRIORITY, ERROR_RUN_PRIORITY]:
            raise j.exceptions.Input("priority should {} or {}, {} given".format(
                             NORMAL_RUN_PRIORITY,
                             ERROR_RUN_PRIORITY,
                             priority))

        if not self._accept:
            raise j.exceptions.RuntimeError("{} is stopping, can't add new run to it".format(self))

        self.logger.debug("add run {} to {}".format(run.model.key, self))
        await self.queue.put((priority, run))

    async def _retry(self, run):
        async def do_retry(run):

            # remove this task from the retries list
            with await self._retries_lock:
                current_task = asyncio.Task.current_task()
                if current_task in self._retries:
                    self._retries.remove(current_task)

            retry_level = run.get_retry_level()
            retry_config = self.get_run_retries(run.retries)
            # if error number exceed size of config won't reschedule
            if retry_level > len(retry_config):
                self.logger.info("Reached max numbers of retries configured")
                return
            else:
                delay = retry_config[retry_level]

            self.logger.info("reschedule run %s in %ssec", run.model.key, delay)
            await asyncio.sleep(delay)

            # sending this action to the run queue
            self.logger.debug("add run %s to %s", run.model.key, self)
            await self.repo.run_scheduler.add(run, ERROR_RUN_PRIORITY)

        # don't add if we are stopping the server
        if not self._accept:
            self.logger.warning("%s is stopping, can't add new run to it", self)
            return
        # add the rery to the event loop
        with await self._retries_lock:
            self._retries.append(asyncio.ensure_future(do_retry(run)))

    def __repr__(self):
        return "RunScheduler<{}>".format(self.repo.name)
