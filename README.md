# PORTEX-TS

PORTEX-TS software package installation guide

### System package upgrade:
$ sudo apt update  
$ sudo apt dist-upgrade  
$ sudo apt -y install python-pip  
$ sudo pip install --upgrade pip  

### Necessary package installation:
$ sudo apt -y install dialog git minicom tmux whois ntpdate   
$ sudo pip install tacacs_plus RPi.GPIO   

### Local user account creation
$ sudo useradd --home /home/portex --shell /usr/local/bin/taclogin -G dialout -m -U portex   

### PORTEX-TS program installation
$ cd /tmp  
$ git clone https://github.com/xinguard/PORTEX-TS.git  
$ cd PORTEX-TS   
$ sudo /bin/bash setup.sh  

### System service register
$ sudo update-rc.d led-daemon defaults  
$ sudo update-rc.d pwr-and-control-button-monitor defaults  
$ sudo sed -i '19a/usr/local/bin/portex_ts.init\n' /etc/rc.local  
  
### Cron table setup for watchdog
$ sudo 
$ sudo /bin/bash -c "(crontab -l 2>/dev/null; echo '* * * * * /usr/local/bin/usbcheck') | crontab -"  
$ sudo /bin/bash -c "(crontab -l 2>/dev/null; echo '* * * * * /usr/local/bin/regreport') | crontab -"   

### Reboot
$ sudo shutdown -r now  
  
