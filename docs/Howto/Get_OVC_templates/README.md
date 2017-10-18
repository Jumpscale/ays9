## OVC templates

To use OVC templates, which are templates used to perform various actions on OpenVCloud environments(like creating a cloudspace,vm, ...) you need to add the actor templates to your system.

This can be done by executing the following code in a js9 shell(type `js9` in the command line), in this instance it will clone from master:

```python
ayscl = j.clients.atyourservice.get()
ayscl.api.ays.addTemplateRepo(data={'url': 'https://github.com/openvcloud/ays_templates','branch': 'master'})

```
For more information about using the templates check the docs [here](https://github.com/openvcloud/ays_templates/tree/master/docs) or for docs for a specific template check `README.md` in each template directory [here](https://github.com/openvcloud/ays_templates/tree/master/templates).
