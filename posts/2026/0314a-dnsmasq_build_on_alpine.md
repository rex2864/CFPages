## dnsmasq build on alpine

예전에 진행했었던 것인데 백업용으로 작성해둔다.

### setup environment

as root

#### build tools

```bash
apk add build-base
apk add cmake
apk add m4
apk add perl
apk add bison
apk add flex
```

#### linux headers and bsd compatable headers

```bash
apk add linux-headers
apk add bsd-compat-headers
```

#### dev packages

```bash
apk add readline-dev
apk add zlib-dev
```

#### make 'dnsmasq' user and login to 'dnsmasq'

```bash
cd ~
mkdir work
```

#### build gmp (GNU MP)

```bash
cd ~/work
wget https://ftp.gnu.org/gnu/gmp/gmp-6.2.1.tar.xz
tar xJf gmp-6.2.1.tar.xz
cd gmp-6.2.1.tar.xz
mkdir build
cd build
../configure --prefix=/home/dnsmasq --enable-cxx --disable-static
make
make check
make install
```

#### build nettle

```bash
cd ~/work
wget https://ftp.gnu.org/gnu/nettle/nettle-3.8.tar.gz
tar xzf nettle-3.8.tar.gz
cd nettle-3.8
mkdir build
cd build
../configure --prefix=/home/dnsmasq --disable-static --with-include-path=/home/dnsmasq/include --with-lib-path=/home/dnsmasq/lib
make
make check
make install
cd ~/lib/
chmod +x libhogweed.so.6.5 libnettle.so.8.5
```

#### build dnsmasq

```bash
cd ~/work
wget https://thekelleys.org.uk/dnsmasq/dnsmasq-2.89.tar.gz
tar xzf dnsmasq-2.89.tar.gz
cd dnsmasq-2.89
```

edit Makefile like below:
- `PREFIX` set to '/home/dnsmasq'
- `COPTS` set to '-DHAVE_DNSSEC'
- comment out `nettle_cflags`, `nettle_libs` and `gmp_libs`
- set `nettle_cflages` to '-I/home/dnsmasq/include'
- set `nettle_libs` to '-L/home/dnsmasq/lib -lnettle -lhogweed'
- set `gmp_libs` to '-L/home/dnsmasq/lib -lgmp`

(optional) start with 'sum' lines check 'dnsmasq.h' that related with nettle header file.
- add '-I/home/dnsmasq/include' before '-E $(top)/$(SRC)/dnsmasq.h'

```bash
make
make install
```

#### make configuration files for dnsmasq

```bash
cd ~
mkdir etc
touch etc/block.hosts
cat >> etc/custom.hosts << END
#format: IPaddr domain1 domain2
#example: 127.0.0.1 localhost.localdomain
END
```

```bash
cat >> etc/dnsmasq.conf << END
domain-needed
expand-hosts
bogus-priv
no-resolv
no-poll
localise-queries
local-service

dnssec
trust-anchor=.,20326,8,2,E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D

user=dnsmasq
group=dnsmasq
cache-size=10000

#server=127.0.0.1#5335
server=1.1.1.1
server=1.0.0.1

server=/test/
server=/localhost/
server=/invalid/

addn-hosts=/home/dnsmasq/etc/custom.hosts
addn-hosts=/home/dnsmasq/etc/block.hosts
END
```

#### make script for periodic update block list

```bash
cd ~/bin

cat >> update_block_lists.sh << END
#!/bin/sh

#below file came from https://github.com/blocklistproject/Lists
wget https://blocklistproject.github.io/Lists/everything.txt -O /home/dnsmasq/etc/block.hosts
rc-service dnsmasq reload
END

chmod +x update_block_lists.sh
```

#### make init script for dnsmasq

```bash
cd ~
mkdir init
```

```bash
cat >> init/dnsmasq.init << END
#!/sbin/openrc-run

description="A lightweight DNS, DHCP, RA, TFTP and PXE server"

extra_commands="checkconfig"
description_checkconfig="Check configuration syntax"

extra_started_commands="reload"
description_reload="Clear cache and reload hosts files"

export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}:/home/dnsmasq/lib

command="/home/dnsmasq/sbin/dnsmasq"
command_args="--keep-in-foreground --conf-file=\$cfgfile"
command_background="yes"
pidfile="/run/\$RC_SVCNAME.pid"

depend() {
        provide dns
        need localmount net
        after bootmisc dbus
        use logger
}

start_pre() {
        \$command --test --conf-file="\$cfgfile" >/dev/null 2>&1 \\
                || return 1
}

reload() {
        ebegin "Reloading \$RC_SVCNAME"
        \$command --test --conf-file="\$cfgfile" >/dev/null 2>&1 \\
                || return 1
        start-stop-daemon --signal HUP --pidfile "\$pidfile"
        eend \$?
}

checkconfig() {
        ebegin "Checking \$RC_SVCNAME configuration"
        \$command --test --conf-file="\$cfgfile"
        eend \$?
}
END
chmod +x init/dnsmasq.init
```

```bash
cat >> init/dnsmasq.conf << END
# Configuration for /etc/init.d/dnsmasq

# Path to the dnsmasq configuration file.
cfgfile="/home/dnsmasq/etc/dnsmasq.conf"

# User and group to change to after startup.
user="dnsmasq"
group="dnsmasq"
END
```

#### install/uninstall scripts

```bash
cd ~
```

```bash
cat >> install.sh << END
#!/bin/sh

# adduser
adduser -g dnsmasq -s /sbin/nologin -D -u 801 dnsmasq

# copy files
cp -a bin etc include lib sbin uninstall.sh /home/dnsmasq/
chown -R dnsmasq:dnsmasq /home/dnsmasq/

# install script for periodic updating block list
echo "0  5  *  *  0  /home/dnsmasq/bin/update_block_lists.sh" >> /etc/crontabs/dnsmasq

# install init script
install -o root -g root -m 755 init/dnsmasq.init /etc/init.d/dnsmasq
install -o root -g root -m 644 init/dnsmasq.conf /etc/conf.d/dnsmasq

# install init script
rc-update add dnsmasq default

# start service
rc-service dnsmasq start

# download first block lists
/home/dnsmasq/bin/update_block_lists.sh
END
```

```bash
cat >> uninstall.sh << END
#!/bin/sh

# stop service
rc-service dnsmasq stop

# uninstall init script
rc-update del dnsmasq default

# remove init script
rm -f /etc/init.d/dnsmasq
rm -f /etc/conf.d/dnsmasq

# remove crontab file for dnsmasq
rm -f /etc/crontabs/dnsmasq

# del home directory
rm -rf /home/dnsmasq

# del user
deluser dnsmasq
END
```

```bash
chmod +x *.sh
```

#### clean up and packaging

```bash
cd ~

rm -rf share work

tar czf dnsmasq.tar.gz *
```

---

Date: 2026. 03. 14

Tags: dnsmasq, build, alpine
