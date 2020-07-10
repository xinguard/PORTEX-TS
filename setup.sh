#!/usr/bin/env bash
#
# Setup tool to install programs and update relative files
#

# /etc/udev/rules.d/90-usb-serial.rules
# /etc/init.d/led-daemon
# /home/ssuser/portex_sys.conf
# /home/ssuser/ssuser

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
su -s /bin/bash ssuser -c "cp etc/portex_sys.conf ~ssuser"
su -s /bin/bash ssuser -c "cp etc/.tmux.conf ~ssuser"







