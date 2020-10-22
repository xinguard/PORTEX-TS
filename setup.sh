#!/usr/bin/env bash
#
# Setup tool to install programs and update relative files
#
declare -i REBOOT_FLAG=0
function REBOOT_CHECK() {
    declare REBOOT_ANS
    if [ $REBOOT_FLAG -eq 1 ]; then
        echo ""
        echo -e "Reboot is required to make change worked."
        read -p "Press 'YES' to reboot, other key to pass: " REBOOT_ANS
        if [ "$REBOOT_ANS" = "YES" ]; then
            echo "Raspberry Pi is restarting....."
            /sbin/shutdown -r now
        else
            echo "Configuration change will work after restart"
            echo ""
        fi
    fi
}

# Check virtual account "portex" status
id portex >/dev/null 2>&1 && (echo "Virtual account 'portexp' has already created") || (echo "Create virtual account 'portex'"; useradd --home /home/portex --shell /usr/local/bin/taclogin -G dialout -m -U portex)

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
passwd -d portex >/dev/null 2>&1
service ssh reload

# Check service daemon installation
service led-daemon status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Service led-daemon has already installed."
else
    echo "Install led-daemon service."
    update-rc.d led-daemon defaults
    REBOOT_FLAG=1
fi
service pwr-and-control-button-monitor status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Service pwr-and-control-button-monitor has already installed."
else
    echo "Install pwr-and-control-button-monitor service."
    update-rc.d pwr-and-control-button-monitor defaults
    REBOOT_FLAG=1
fi

# Check booting script installation
grep 'portex_ts.init' /etc/rc.local >/dev/null 2>&1 || (echo "Install booting script"; sed -i '19a/usr/local/bin/portex_ts.init\n' /etc/rc.local)

# Check if reboot is required
REBOOT_CHECK

echo "PORTEX-TS setup process complete"
exit 0
