g8client__uk:
  url: uk-g8-1.demo.greenitglobe.com
  login: *****
  password: *****
  account: *****

uservdc__yves:
  g8client: uk
  email: yves.kerwyn@greenitglobe.com
  provider: itsyouonline

vdc__vdc4yves:
  g8client: uk
  location: uk-g8-1
  uservdc:
    - yves

node.ovc__vm4yves:
  bootdisk.size: 20
  memory: 1
  os.image: Ubuntu 16.04 x64
  vdc: vdc4yves

autosnapshotting__snapshotting4yves:
  snapshotInterval: 1h
  cleanupInterval: 1d
  retention: 3d
  vdc: vdc4yves

actions:
  - action: install
