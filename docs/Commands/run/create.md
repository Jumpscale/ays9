# ays run create


```shell
ays run create --help
Usage: ays run create [OPTIONS]

  Look for all action with a state 'schedule', 'changed' or 'error' and
  create a run. A run is an collection of actions that will be run on the
  repository.

Options:
  -y, --yes, --assume-yes  Automatic yes to prompts. Assume "yes" as answer to
                           all prompts and run non-interactively
  --force                  force execution even if no change
  --debug                  enable debug in jobs
  --profile                enable profiling of the jobs
  -f, --follow             follow run execution
  -c, --callback TEXT      callbackUrl to which run state will be sent after
                           the run is finished
  --help                   Show this message and exit.

```

## Callback url

The url specified in this option will be used to send the state information of the run. A post request will be sent to the url containing the run id and the run state after the run has either failed or succeeded.

```toml
!!!
title = "AYS Run Create"
tags= ["ays"]
date = "2017-03-02"
categories= ["ays_cmd"]
```
