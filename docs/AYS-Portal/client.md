
### Generate Client for AYS REST API:
- Install go-raml : https://github.com/Jumpscale/go-raml#install
- Generate client code from raml specifications
```
go-raml client -l python --dir client --ramlfile jscockpit/ays_api/specifications/ays.raml
```
- Edit the client.py file and update the `BASE_URI`

#### How to use:
```python
jwt = "jwt from itsyou.online"
cl = Client()
cl.BASE_URI = 'https://mycockpit.com/api'
resp = cl.listRepositories(headers={"Authorization": "token " + jwt})
resp.json()
```

If you use JumpScale a client is available at `j.clients.cockpit`
