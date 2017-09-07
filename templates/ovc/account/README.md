
# template: ovc.account

## Description:
This actor template is responsible for creating an account on any openVCloud environment.

## Schema:

- description: Arbitrary description of the account. **Optional**

- g8client: Name of the g8client used to connect to the environment.

- accountusers: List of uservdcs that will be authorized on the account.

- accountID: The ID of the account. **Filled in automatically, don't specify it in the blueprint**

- maxMemoryCapacity: The limit on the memory capacity that can be used by the account. Default: -1 (unlimited)

- maxCPUCapacity: The limit on the CPUs that can be used by the account. Default: -1 (unlimited)

- maxNumPublicIP: The limit on the number of public IPs that can be used by the account. Default: -1 (unlimited)

- maxDiskCapacity: The limit on the disk capacity that can be used by the account. Default: -1 (unlimited)

- consumptionFrom: determines the start date of the required period to fetch the account consumption info from. If left empty will be creation time of the account.

- consumptionTo: determines the end date of the required period to fetch the account consumption info from. If left empty will be consumptionfrom + 1 hour.

- consumptionData: consumption data will be saved here as series of bytes which represents a zip file. Example of writing the data:
```
service = response.json() # response is the service view that can be obtained from getServiceByName
with open('/tmp/account.zip', 'wb') as f:
    f.write(service['data']['consumptionData'])
```

## Add/remove/update user

It is possible to add, remove and update user access to the account. To add a user after creating the account, a new uservdc has to be added in the blueprint. Executing the blueprint will trigger the process change and add it to the account. In the same way a user can be removed from the account by deleting the entry from the accountusers in the blueprint. Changing the accesstype of as user will update the user access to the account when executing the blueprint.

## Example for creating an account

```yaml
g8client__env:
  url: '<env_url>'
  login: '<username>'
  password: '<password>'

uservdc__<username>:

account__acc:
  description: 'test account'
  g8client: 'env'
  accountusers:
    - name: '<username>'
      accesstype: '<accesstype>'
  maxMemoryCapacity: <value>
  maxCPUCapacity:  <value>
  maxDiskCapacity: <value>
  maxNumPublicIP: <value>

actions:
  - action: install
```

## Example for adding user 'usertest' to account

```yaml
uservdc__usertest:
    password: 'test1234'
    email: 'fake@example.com'
    groups:
      - 'user'
    g8client: 'env'

account__acc:
  accountusers:
      - name: '<username>'
        accesstype: '<accesstype>'
      - name: 'usertest'
        accesstype: '<accesstype>'

```

## Example for changing access rights of user 'usertest'

```yaml
account__acc:
  accountusers:
      - name: '<username>'
        accesstype: '<accesstype>'
      - name: 'usertest'
        accesstype: '<changed_accesstype>'

```

## Example for removing user 'usertest' from account

```yaml
account__acc:
  accountusers:
    - name: '<username>'
      accesstype: '<accesstype>'
```

## Example for updating the limits of the account

```yaml
account__acc:
    maxMemoryCapacity: <changed_value>
    maxCPUCapacity: <changed_value>
    maxDiskCapacity: <changed_value>
    maxNumPublicIP: <changed_value>
```


## Example for listing disks associated with account:

```yaml

g8client__env:
    url: '<env-url>'
    login: '<login user>'
    password: '<login password>'

account__account1:

actions:
  - action: install
    actor: g8client
    service: env
  - action: list_disks
    actor: account
    service: account1
```

## Example for getting consumption info

```yaml

g8client__env:
  url: '<env-url>'
  login: '<login user>'
  password: '<login password>'

account__acc:
  description: 'test account'
  g8client: 'env'
  consumptionFrom: <start epoch>
  consumptionTo: <end epoch>

actions:
  - action: get_consumption
```
