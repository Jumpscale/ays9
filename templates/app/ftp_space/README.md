# template: ftp_space

## Description:

This actor template is a helper service for the ftp service to allow creation of 1 to many ration for ftp server to
spaces.
## Schema:
 - path : type:string default is '/mnt/storage' of root path of the ftp server
 - authorized_users : type:list of strings of authorized users
 - permission : type:string permission strings as explained below

   permissions:
```
        Read permissions:
        "e" = change directory (CWD, CDUP commands)
        "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands)
        Write permissions:

        "a" = append data to an existing file (APPE command)
        "d" = delete file or directory (DELE, RMD commands)
        "f" = rename file or directory (RNFR, RNTO commands)
        "m" = create directory (MKD command)
        "w" = store a file to the server (STOR, STOU commands)
        "M" = change mode/permission (SITE CHMOD command)
```

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