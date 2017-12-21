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
  -r, --retries TEXT       Configuration for run scheduler as comma separated
                           values
  --help                   Show this message and exit.
```

## Callback url

The url specified in this option will be used to send the state information of the run. A post request will be sent to the url containing the run id and the run state after the run has either failed or succeeded.

## Retries Configuration

The values specified using this option will be configure the delays of the run scheduler as well as the number of retries for that specific run. The number of retries will depend on the number of values specified. If the option is not specified it will use the default configuration see run [docs](../../Definitions/Runs.md). An example configuration which will set the number of retries to 4:

```shell
ays run create --retries 10,30,60,120
```

To prevent retries altogether:

```shell
ays run create --retries 0
```

```toml
!!!
title = "AYS Run Create"
tags= ["ays"]
date = "2017-03-02"
categories= ["ays_cmd"]
```
