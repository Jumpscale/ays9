## CURL Examples

### Get an access token

curl -d "grant_type=client_credentials&client_id=artiliumv2&client_secret=ge9Qw99EPDiTYrt-vzpooPKIaUshoeneK70UVqxpoh2Qg2HfOvbg" https://itsyou.online/v1/oauth/access_token

### Get a JWT

curl -H "Authorization: token 3x-cgmEzNbRYr7z8lgK96akuq0Jd" https://itsyou.online/v1/oauth/jwt?aud=artiliumv2


### List all repositories

curl -X GET -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository


### Create a repository

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" -H "Content-Type: application/json" -d '{"name":"yves02", "git_url":"git@github.com:yveskerwyn/cockpit_repo_yves.git"}' https://artilium.aydo2.com/api/ays/repository


### Get repository details

curl -X GET -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves


### Delete a repository

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves


### List all blueprints

curl -X GET -H "Authorization: bearer $JWT$" https://cl.aydo2.com/api/ays/repository/yves/blueprint


### Delete a blueprint

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/vdc4yves.yaml


### Create blueprint for a g8client service

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" -H "Content-Type: application/json" -d '{"name":"uk.yaml","content":"g8client__uk:\n  instance: main\n  account: *****"}' https://artilium.aydo2.com/api/ays/repository/yves01/blueprint


### Delete g8client blueprint

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/uk.yaml


### Execute g8client blueprint

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository/yves01/blueprint/uk.yaml


### Delete g8client service (undoes above execution)

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/service/g8client/uk


### Blueprint for uservdc

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"yves.yaml","content":"uservdc__yves:\n  g8client: uk\n  email: yves.kerwyn@greenitglobe.com\n  provider: itsyouonline"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute uservdc blueprint

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/yves.yaml


### Blueprint with install action for uservdc service

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"user-actions.yaml","content":"actions:\n  - action: install\n    actor: uservdc\n    service: yves"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute install action blueprint for uservdc service

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/user-actions.yaml


### Create and execute run on repository

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/aysrun


### Blueprint with uninstall action for uservdc service

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"user-actions2.yaml","content":"actions:\n  - action: uninstall\n    actor: uservdc\n    service: yves"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute uninstall action blueprint for uservdc service

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/user-actions2.yaml


### Blueprint for creating a VDC (excluding the actions block)

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" -H "Content-Type: application/json" -d '{"name":"vdc4yves2.yaml","content":"vdc__vdc4yves2:\n  g8client: uk\n  account: CentriLogic Account\n  location: uk-g8-1"}' https://artilium.aydo2.com/api/ays/repository/yves03/blueprint

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" -H "Content-Type: application/json" -d '{"name":"vdc4yves3.yaml","content":"vdc__vdc4yves3:\n  g8client: uk\n  location: uk-g8-1"}' https://artilium.aydo2.com/api/ays/repository/yves03/blueprint

### Execute VDC blueprint (excluding actions)

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository/yves03/blueprint/vdc4yves2.yaml

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository/yves03/blueprint/vdc4yves3.yaml

### Blueprint only defining actions

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" -H "Content-Type: application/json" -d '{"name":"actions.yaml","content":"actions:\n  - action: install"}' https://artilium.aydo2.com/api/ays/repository/yves01/blueprint


### Execute actions blueprint

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository/yves01/blueprint/actions.yaml

### Blueprint for creating a VDC (including the actions block)

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"vdc4yves.yaml","content":"vdc__vdc4yves:\n  g8client: uk\n  location: uk-g8-1\nactions:\n  - action: install"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Delete a blueprint

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/vdc4yves.yaml


### Execute a blueprint

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/vdc4yves.yaml

### Delete service (undoes the execution)

curl -X DELETE -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/service/vdc/vdc4yves


### Create a run

curl -X POST -H "Authorization: bearer eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXJ0aWxpdW12MiIsImFydGlsaXVtdjIiXSwiZXhwIjoxNDgwMzUzMDg0LCJnbG9iYWxpZCI6ImFydGlsaXVtdjIiLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6W119.-ozo2xI0wepqmSGVUrNNSgEXRN1hKxg-VSfoR-7n1iNDLpn035DucKyxz5VD6cxwcWojsgqdRMR_Q1xWN2HNG6MblubZ57gcNk7IQQaWyGy9jm3DG6m3wu9o9Y95AIk9" https://artilium.aydo2.com/api/ays/repository/yves01/aysrun


### List all runs

curl -X GET -H "Authorization: bearer $JWT$" https://cl.aydo2.com/api/ays/repository/yves2/aysrun


## Blueprint for creating a VM (using memory:2 instead of os.size: 1)

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"vm4yves.yaml","content":"node.ovc__vm4yves:\n  bootdisk.size: 20\n  memory: 1\n  os.image: Ubuntu 16.04 x64\n  vdc: vdc4yves"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute VM blueprint

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/vm4yves.yaml


### Blueprint with install action for VM service

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"vm-actions.yaml","content":"actions:\n  - action: install\n    actor: node.ovc\n    service: vm4yves"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute install action blueprint for VM service

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/vm-actions.yaml


### Create and execute run on repository

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/aysrun


## Blueprint for autosnapshotting, including install action

curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"autosnapshotting.yaml","content":"autosnapshotting__snapshotting4yves:\n  snapshotInterval: 1h\n  cleanupInterval: 1d\n  retention: 3d\n  vdc: vdc4yves\nactions:\n  - action: install\n    actor: autosnapshotting\n    service: snapshotting4yves"}' https://cl2.aydo2.com/api/ays/repository/yves/blueprint


### Execute autosnapshotting blueprint

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/blueprint/autosnapshotting.yaml


### Create a run

curl -X POST -H "Authorization: bearer $JWT$" https://cl2.aydo2.com/api/ays/repository/yves/aysrun
