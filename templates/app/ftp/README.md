# template: ftp

## Description:

This actor template creates an ftp server running on the specified node with the specified subvolmes, users, passwords,
 and permissions.These params are specified per ftp_space a helper service for the ftp service.The server uses a
python library pyftp server and runs on port 2121 on the specified node.

## Schema:
 - os : type:string os service name , required.
 - fs : type:string fs service name.
 - spaces : type:list of strings ftp_space service names.

## Example:

```yaml
sshkey__key1:

node.physical__nodevm1:
   ip.public: 'ip'
   ssh.login: 'login'
   ssh.password: 'password'
   sshkey: 'key1'
   ssh.port: 22

os.ssh.ubuntu__osvm1:
  sshPort: 22
  sshkey: 'key1'
  node: 'nodevm1'

fs.btrfs__fsvm1:
    os: 'osvm1'
    mount: '/mnt/storage/'

# ftp configuration
ftp_space__space1vm1:
    path: '/mnt/storage/pool1'
    authorized_users:
        - 'gig:mysecret'
        - 'root:othersecret'
    permission: 'elrmw'

ftp__ftpvm1:
    os: 'osvm1'
    fs: 'fsvm1'
    spaces:
        - 'space1vm1'
```