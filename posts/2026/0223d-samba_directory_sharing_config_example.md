## samba directory sharing config exampled

```
[disk1]
   comment = disk1
   path = [path to directory, ex) /mnt/disk1]
   guest ok = no
   browseable = yes
   read only = no
   create mask = 0644
   directory mask = 0755
   valid users = [userid]
```
