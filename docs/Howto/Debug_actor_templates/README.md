# Debug Actor Templates

During the development of your actor template you will probably want to use tools like `ipdb` to jump into the execution of the actions code and inspect the state of the services. But since AYS uses multiprocessing to improve the execution speed of the actions these tools don't work.

To force the execution of your action in process and thus allow utilisation of the debugger, follow the below steps.

Update the `actions.py` of your local actor template:
```bash
cd ActorTemplates
vim <actor-name>/actions.py
```

Add the breakpoint:
```python
import ipdb; ipdb.set_trace()
```

Update the actor from the updated actor template:
```bash
ays actor update --name <actor-name>
```

Schedule execution of the updated action:
```bash
ays action <action-name> --force --actor <actor-name> --service <service-name>
```

Create a new run:
```bash
ays run create
```

You get to the breakpoint:
```bash
ipdb>
```
