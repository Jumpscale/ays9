# template: uservdc

## Description

This template represents a user on an environment. If the user doesn't exist it will be created.

## Schema

- password: Password of the user.
- email: Email of the user.
- provider: Oauth provider. Currently: itsyou.online
- groups: Groups that the user will belong to.
- g8client: User login.

## Example

```yaml
g8client__example:
    url: '<url of the environment>'
    login: '<username>'
    password: '<password>'
    account: '<account name>'

uservdc__ex:
    password: '<password>'
    email: '<email>'
    provider: 'itsyouonline'
    groups: '<list of groups>'
    g8client: 'example'
    
actions:
  - action: install
```
