# Start the AYS Portal

When using the JS9 Docker container, first make sure your container is joined to a ZeroTier network, as documented in [Join Your ZeroTier Network](zt.md).

Then start the JumpScale interactive shell:
```shell
js9
```

In the JumpScale interactive shell ('js9') execute:
```python
prefab = j.tools.prefab.local
prefab.js9.atyourservice.install()
```

This will install and start the AYS Portal on port 8200, as pre-configured in `/opt/cfg/portals/main/config.yaml`, which is the configuration common to all portals using the JumpScale Portal Framework of your JumpScale environment. See [AYS Portal Configuration](../AYS-Portal/README.md) for more details.

When attaching to the main TMUX session, you'll see that two additional TMUX windows have been added, one for MongoDB and another one for the Portal:
```shell
tmux at
```

Use CTRL+B 1, 2 or 3 to toggle between the TMUX windows.

In order to activate ItsYou.online integration, you need to change the following entries:

```yaml
force_oauth_instance: 'itsyouonline'
production: true

oauth.redirect_url: 'http://172.25.226.34:8200/restmachine/system/oauth/authorize'
oauth.client_scope: 'user:email:main,user:memberof:organization-2'
oauth.organization: 'organization-2'
oauth.client_id: 'organization-3'
oauth.client_secret:  '****'
```

See [Installation of an AYS Portal](../AYS-Portal/installation/README.md) for details on how to use these configuation keys.

> Note that you can specify for the same organization, in both `oauth.client_scope`, `oauth.organization` and `oauth.client_id`, and that it can actually be the same organization as specified when configuring the API Server, as documneted in [Start AYS](startays.md)

Once updated restart the portal, typically by stopping the portal with CTRL+C in the TMUX window and simply re-executing  the last command.

Alternativelly you can do it manually:
```shell
cd /opt/jumpscale9/apps/portals/main
python3 portal_start.py
```

Also see the [AYS Portal](../AYS-Portal/README.md) documentation.
