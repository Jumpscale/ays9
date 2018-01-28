# Generate ItsYou.online JWT

```shell
ays generatetoken --help
Usage: ays generatetoken [OPTIONS]

Options:
 --clientid TEXT      client_id
 --clientsecret TEXT  client_secret
 --organization TEXT  Organization
 --help               Show this message and exit.
```

Example:

```
root@js9:/host/var/ays_repos/grid# ays generatetoken --clientid='rgergerger' --clientsecret='ergerger' --organization='deboeckj'
# Generated Token, please run to use in client:
export JWT='eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJjT2JQRHdJakE5anFYQUJegfwgergerZYUk2WVZOQXVaZXpHIiwiZXhwIjoxNDk3NjE1OTk2LCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJyZWZyZXNoX3Rva2VuIjoiUFJXUFZYWVM2eU5jUVMwR3NEWHdtdlJZa3U0WCIsInNjb3BlIjpbInVzZXI6bWVtYmVyb2Y6ZGVib2Vja2oiXSwidXNlcm5hbWUiOiJkZWJvZWNraiJ9.xhgf5mIFsQZG0aCs4Qewrd2mMlrLshuNmWuGLYPRYvPRNAnjmaH7_4LR20-C54AqY6fw5cOve5Mz6CESZQpukWIHrIXBzoijl8WsBrcMsjD1ZnpeqgZEbQRpFJVCB0Nr'
```
