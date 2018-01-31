# S3 Umbrella Package

The S3 Umbrella Package is AYS actor template for installing and configuring a Scality S3 server.

See [How to create a S3 server](https://gig.gitbooks.io/cockpit/content/usage/Howto/Create_S3server/Create_S3server.html) in the [G8 Cockpit Documentation](https://www.gitbook.com/book/gig/cockpit/details) for detailed instructions on how to use this actor template.


## Blueprint

```
g8client__{environment}:
  instance: '{ovc_config_instance(i.e. main)}'
  account: '{account}'

vdc__{vdc-name}:
  g8client: '{environment}'
  account: '{account}'
  location: '{location}'

sshkey__{sshkey-name}:

disk.ovc__{disk-name}:
  size: {size}

s3__{s3server}:
  vdc: {vdc-name}
  sshkey: '{sshkey-name}''
  disk:
    - '{disk-name}'
  hostprefix: 'host-prefix'
  key.access: '{access}'
  key.secret: '{secret}'
  enablehttps: '{True | False}'

actions:
  - action: 'install'
```  

Values:

- `{environment}`: environment name for referencing in the blueprint
- `{url}`: URL to to the G8 environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the targeted G8 environment
- `{password}`: password for the username
- `{account}`: account on the targeted G8 environment used for the S3 server
- `{vdc-name}`: VDC that will be created for the S3 server
- `{location}`: location where the VDC needs to be created
- `{sshkey-name}`: name of the SSH key that will be created
- `{disk-name}`: name of the disk that will be created; you ca create multiple disks
- `{size}`: disk size in GB, for more details see
- `{hostprefix}`: the first part in your app URL, i.e `hostprefix` in the FQDN `hostprefix-machinedecimalip.gigapps.io`; the remaining part of the FQDN will be calculated, for more information see https://github.com/0-complexity/ipdns
- `{key.access}`: S3 access key (username); will be auto-generated when not set  
- `{key.secret}`: S3 access secret (password); will be auto-generated when not set
- `{enablehttps}`: to enable https; when omitted will default to False


> NOTE: Scality doesn't work well with `CyberDuck` the s3 client. To test Scality, use `s3cmd`

## s3cmd config

```ini
[default]
access_key = accessKey1
secret_key = verySecretKey1

host_base = FQDN
host_bucket = FQDN

signature_v2 = True
use_https = False
```

Set the `host_base` and `host_bucket` to the value of `fqdn` which will be available after the installation.
