# Join Your ZeroTier Network

First check the status of the ZeroTier daemon:
```shell
zerotier-cli info
```

In case the ZeroTier daemon is not running yet, you'll get following error: `zerotier-cli: missing port and zerotier-one.port not found in /var/lib/zerotier-one`, in order to launch the ZeroTier daemon execute:
```shell
zerotier-one -d
```

Check if your container already joined a ZeroTier network:
```shell
zerotier-cli listnetworks
```

If no ZeroTier network was yet joined, join your ZeroTier network:
```shell
export ZEROTIER_NETWORK_ID="..."
zerotier-cli join $ZEROTIER_NETWORK_ID
```

You will now need to go to `https://my.zerotier.com/network/$ZEROTIER_NETWORK_ID` in order to authorize the join request.

This will allow you to SSH into the container on ZeroTier network address:
```shell
exit
ssh -A root@<ZeroTier network address>
```

If you started AYS as documented in [Start AYS](startays.md) you will now be able to interact with the AYS RESTful API.

Next you might want to install and start JumpScale Portal, allowing you to interact with the AYS Portal, as documented in [Start the AYS Portal](portal.md).
