# Long running jobs

AYS is written using asyncio technique to achieve concurrency.

## Introduction
You can have long running tasks aka `recurring tasks` and it'll serve you well to a limit as it uses `loop.run_in_executor` to not block `ays main thread`, if you are having too much long running jobs maybe you need to use `LongRunningTask` concept.

## How it Works
You basically define a coroutine to be `injected` in the main loop, which is `DANGEROUS`, because again, you will end in a `blocked AYS server`.


## How to define a `Long Running Task`

in `actions.py` of your service.
```

def long1(job):
    print("JOB LONG1 STARETED ACTIONS FILE")
    from asyncio import sleep, get_event_loop
    async def inner(job):
        print(">>>>>before sleep 20")
        await sleep(20)
        print(">>>>>>>>>>> after sleep 20")
        await sleep(25)
        print(">>>>>>>>>> after sleep 25")
        await sleep(100)
        print(">>>> after 100 seconds")
        while True:
            print("IN LOOP")
            await sleep(1)
    return inner(job)
```
in `config.yaml` you specify the long running jobs

```
longjobs:
    - action: long1
```
