#! /bin/bash
echo -e "green_blink\c" | sudo nc -q 1 -U /var/run/uds_led
echo -e "red_on\c" | sudo nc -q 1 -U /var/run/uds_led
#apt-get update
#apt-get -y install tnlctl cbox-panel-control minicom
sleep 3
#/opt/mcs/cbox_panel_control/bin/regcheck > /dev/null &
/usr/local/bin/gwcheck > /dev/null &
#/opt/mcs/cbox_panel_control/bin/tnlcheck > /dev/null &
/usr/local/bin/tscheck > /dev/null &
echo -e "green_on\c" | sudo nc -q 1 -U /var/run/uds_led
service bluetooth stop
