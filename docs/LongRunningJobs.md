# Long running jobs

AYS is written using asyncio technique to achieve concurrency.

## Introduction
You can have `recurring tasks` and it'll serve you well to a limit as it's uses `loop.run_in_executor`, so It'll be mapped to a thread which requires a lot of resources compared to a coroutine.

If you are having plenty of `long running tasks` you can make use of `LongRunningTask` feature in `AYS` to overcome the limits of `recurring tasks`.

## How it Works
a `LongRunningTask` is a coroutine to be executed in the AYS main loop.

## How to define a `Long Running Task`

in `actions.py` of your service.
```

def long2(job):
    # check if key "shouldstop" is set in redis
    async def inner(job):
        import aioredis
        from asyncio import sleep, get_event_loop
        loop = get_event_loop()
        redis = await aioredis.create_redis(('localhost', 6379), loop=loop)
        while True:
            job.logger.info("Checking for shouldstop key: ")
            val = await redis.get('shouldstop')
            if val == b"1":
                job.logger.info("Should stop executing now.")
                redis.close()
                await redis.wait_closed()
                break
            await sleep(1)
        job.logger.info("Completed execution of long job long2")
    return inner(job)

```

```
longjobs:
    - action: long2
```


> Note: code in inner needs to be fully async or the code will block AYS main loop.

in `config.yaml` you specify the long running jobs
