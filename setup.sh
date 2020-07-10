#!/usr/bin/env bash
#
# Setup tool to install programs and update relative files
#

# Install programs to /usr/local/bin
for file in `ls bin`
do
    cp bin/$file /usr/local/bin
done

# Install program to /etc
cp etc/90-usb-serial.rules /etc/udev/rules.d
cp etc/led-daemon /etc/init.d
cp etc/ssuser /etc/sudoers.d

# Install configuration files for ssuser
[ ! -f ~ssuser/portex_sys.conf ] && su -s /bin/bash ssuser -c "cp etc/portex_sys.conf ~ssuser"
su -s /bin/bash ssuser -c "cp etc/.tmux.conf ~ssuser"

# Modify sshd configuration for no password login
sed -i 's/^#PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config
sed -i 's/^UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
passwd -d ssuser
service ssh reload






