#!/usr/bin/env bash
#
# Setup tool to install programs and update relative files
#

# Install programs to /usr/local/bin
for file in $(ls bin); do
    cp bin/$file /usr/local/bin
done

# Install program to /etc
cp etc/90-usb-serial.rules /etc/udev/rules.d
cp etc/led-daemon /etc/init.d
cp etc/pwr-and-control-button-monitor /etc/init.d
cp etc/portex_ts /etc/sudoers.d
chmod 440 /etc/sudoers.d/portex_ts

# Install configuration files for portex
[ ! -f ~portex/portex_ts.conf ] && su -s /bin/bash portex -c "cp etc/portex_ts.conf ~portex"
su -s /bin/bash portex -c "cp etc/.tmux.conf ~portex"

# Modify sshd configuration for no password login
sed -i 's/^#PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config
sed -i 's/^UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
passwd -d portex
service ssh reload

# Check service daemon installation
service led-daemon status >/dev/null 2>&1 || (echo "Install led-daemon service"; update-rc.d led-daemon defaults)
service pwr-and-control-button-monitor status >/dev/null 2>&1 || (echo "Install pwr-and-control-button-monitor service"; update-rc.d pwr-and-control-button-monitor defaults)

# Check booting script installation
grep 'portex_ts.init' /etc/rc.local >/dev/null 2>&1 || (echo "Install booting script"; sed -i '19a/usr/local/bin/portex_ts.init\n' /etc/rc.local)

# Check cron job installation
crontab -l 2>/dev/null | grep usbcheck >/dev/null || (echo "Install cron job usbcheck"; /bin/bash -c "(crontab -l 2>/dev/null; echo '* * * * * /usr/local/bin/usbcheck') | crontab -")
crontab -l 2>/dev/null | grep regreport >/dev/null || (echo "Install cron job regreport" && /bin/bash -c "(crontab -l 2>/dev/null; echo '* * * * * /usr/local/bin/regreport') | crontab -")
