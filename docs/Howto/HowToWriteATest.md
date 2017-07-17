# Howto Write an AYS test

Tests are AYS driven meaning they are going to be executed within AYS server.

## Writing a test
- Create a repo under `tests` directory `i.e` with actorTemplates and blueprints and related blueprints (to create instance of your actorTemplates).
- Create a test actortemplate under `tests/test_services`
- In `bp_test_templates` create a blueprint to create a service.


## Test ActorTemplate

Contains a `result` attribute
```
@0xbbdf7d0b0b5c4c52; # make sure to generate a new ID
struct Schema {
	result @0 :Text;

}
```
Make sure to execute the initialization blueprints of your test repository to reach the state you are testing.


## Running the test suite manually
start `js9` shell in `ays9` directory
```
import testrunner
testrunner.main()

```


## Example
Testing the `LongRunningTask`


- ### Test repository

  1- Create a repo `sample_repo_longjobs`

  2- Create an actorTemplate `longjobsact` with a long running task in `actions.py` and setting it in its `config.yaml`

  `config.yaml`
  ```
  longjobs:
      - action: long1
        depends: []

  ```
  `actions.py`
  ```
  def long1(job):
      print("JOB LONG1 STARETED")
      from asyncio import sleep, get_event_loop
      async def inner(job):
          while True:
              print("IN LOOP")
              await sleep(5)
      return inner(job)
  ```

  3- Create a blueprint `blueprints/test_longjobsact.yaml` to reach that state which in this case only creating an instance of longjobsact

  ```
  longjobsact__la:
  ```

- ###  Test actorTemplate

  1- under `test_services` we created `test_longjobs_actions` actorTemplate with `schema.capnp` and `actions.py`

  2- In `schema.capnp` file contains a result attribute to store our test result.

  ```
  @0xbbdf7d0b0b5c4c52; # make sure to generate a new ID
  struct Schema {
  	result @0 :Text;

  }
  ```
  3- In `actions.py` we create a reasonable test scenario
  ```
  def test(job):
      """
      Test long actions
      """
      import sys
      import time
      RESULT_OK = 'OK : %s'
      RESULT_FAILED = 'FAILED : %s'
      RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
      model = job.service.model
      model.data.result = RESULT_OK % job.service.name
      failures = []
      # HERE create run in sample_repo_timeout and wait for 10 seconds and check if the actions timedout.
      try:
          repo = 'sample_repo_longjobs'
          cl = j.clients.atyourservice.get().api.ays
          # will try to execute a `longjob1` in main thread to make sure it doesn't block
          start = time.time()
          cl.executeBlueprint(data=None, repository=repo, blueprint='test_longjobsact.yaml')
          repos = cl.listRepositories().json()
          end = time.time()
          if end - start > 5:   # took more than 2 seconds? should never happen.
              failures.append("AYS server was blocked")

          if failures:
              model.data.result = RESULT_FAILED % '\n'.join(failures)
          else:
              model.data.result = RESULT_OK % 'AYS EXECUTED THE COROUTINE IN THE MAIN THREAD WITH NO PROBLEMS'
      except:
          model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
      finally:
          job.service.save()
          cl.destroyRepository(data=None, repository=repo)

  ```

- ###  Create a test service blueprint
  Under `tests/bp_test_templates` we create `test_longjobs.yaml` to create an instance of `test_longjobs_actions` template and call its `test` action

  ```
  test_longjobs_actions__tlj:

  actions:
    - action: test
  ```
