# Start the AYS Portal

When using the JS9 Docker container, first make sure your container is joined to a ZeroTier network, as documented in [Join Your ZeroTier Network](zt.md).

Then start the JumpScale interactive shell:
```shell
js9
```

In the JumpScale interactive shell ('js9') execute:
```python
prefab = j.tools.prefab.local
prefab.apps.portal.install()
```


This will install and start the AYS Portal on port 8200: http://<Zero-Tier-IP-address>:8200/.

When attaching to the main TMUX session, you'll see that two additional TMUX windows have been added, one for MongoDB and another one for the Portal:
```shell
tmux at
```

Use CTRL+B 1, 2 or 3 to toggle between the TMUX windows.

In order to change the IP address and port on which the portal is reachable or any other portal configuration we'll need to update the portal configuration `/optvar/cfg/portals/main/config.yaml`:

First stop the portal using CTRL+C in the third TMUX window (CTRL+B 2) and then update for instance the value of `ipaddr` and `port` in `/optvar/cfg/portals/main/config.yaml`:


```bash
vi /optvar/cfg/portals/main/config.yaml

mongoengine.connection:
    host: 'localhost'
    port: 27017

rootpasswd: 'admin'

ipaddr: '0.0.0.0'
port: '8200'
appdir: '$JSAPPSDIR/portals/portalbase'
filesroot: '$VARDIR/portal/files'
defaultspace: 'system'
admingroups:
    - 'admin'
authentication.method: 'me'
gitlab.connection: 'main'
force_oauth_instance: ''  # set to use oauth
contentdirs:  ''

production:  False

oauth.client_url:  'https://itsyou.online/v1/oauth/authorize'
oauth.token_url:  'https://itsyou.online/v1/oauth/access_token'
oauth.redirect_url:  'http://ae5d255c.ngrok.io/restmachine/system/oauth/authorize'
oauth.client_scope:  'user:email:main,user:memberof:JSPortal'
oauth.client_id:  'JSPortal'
oauth.client_secret:  '***'
oauth.client_user_info_url:  'https://itsyou.online/api/users/'
oauth.client_logout_url:  ''
oauth.organization: testOrg
oauth.default_groups:
    - admin
    - user
```

Now restart the portal:
```shell
cd /opt/jumpscale9/apps/portals/main
python3 portal_start.py
```

Also see the [AYS Portal](../AYS-Portal/README.md) documentation.
