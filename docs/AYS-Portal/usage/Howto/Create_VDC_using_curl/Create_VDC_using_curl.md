## How to create a VDC using curl

Steps:
- [Get an OAuth token with Client Credentials Flow](#get-token)
- [Get a JWT to talk to the Cockpit](#get-JWT)
- [Create a new repository](#create-repository)
- [Create blueprint for a g8client service instance](#g8client-blueprint)
- [Execute the g8client blueprint](#g8client-execute)
- [Create blueprint for a user](#user-blueprint)
- [Execute the user blueprint](#user-execute)
- [Create blueprint for new VDC](#vdc-blueprint)
- [Execute the VDC blueprint](#vdc-execute)
- [Execute the install action for VDC](#install-VDC)


<a id="get-token"></a>
### Get an OAuth token with Client Credentials Flow

```
curl -d "grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET" /
     https://itsyou.online/v1/oauth/access_token
```

<a id="get-JWT"></a>
### Get a JWT to talk to the Cockpit

```
curl -H "Authorization: token OAUTH-TOKEN" /
     https://itsyou.online/v1/oauth/jwt?aud=client_id
```

<a id="create-repository"></a>
### Create a new repository

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"test-repo"}'
     https://BASE_URL/api/ays/repository
```

<a id="g8client-blueprint"></a>
### Create blueprint for a g8client service instance

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'gig'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/api/ays/repository/
```

<a id="g8client-execute"></a>
### Execute the g8client blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/blueprint/BLUEPRINT-NAME
```

<a id="user-blueprint"></a>
### Create blueprint for a user

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'gig'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/api/ays/repository/
```

<a id="user-execute"></a>
### Execute the user blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/blueprint/BLUEPRINT-NAME
```

<a id="vdc-blueprint"></a>
### Create blueprint for new VDC

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'gig'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/api/ays/repository/
```

<a id="vdc-execute"></a>
### Execute the VDC blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/blueprint/BLUEPRINT-NAME
```

<a id="install-VDC"></a>
### Execute the install action for VDC

```
curl -H "Authorization: bearer JWT"  /
     -d "action=install&async=true&force=false&instance=INSTANCE-NAME&role=ROLE"
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/execute
```
