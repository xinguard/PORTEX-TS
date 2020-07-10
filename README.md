# PORTEX-TS

PORTEX-TS software package installation guide

### System package upgrade:
$ sudo apt-get update  
$ sudo apt-get dist-upgrade  
$ sudo apt-get install python-pip  
$ sudo pip install --upgrade pip  

### Necessary package installation:
$ sudo apt-get -y install minicom tmux whois ntpdate   

### Local user account creation
$ sudo adduser --home /home/ssuser --shell /usr/local/bin/taclogin -m -U ssuser  

### PORTEX-TS program installation
$ cd /tmp  
$ git clone https://github.com/xinguard/PORTEX-TS.git  
$ cd PORTEX-TS   
$ sudo /bin/bash setup.sh  

### System service register
$ sudo update-rc.d led-daemon defaults  
$ sudo update-rc.d pwr-and-control-button-monitor defaults  
$ sudo sed -i '19a/usr/local/bin/portex-ts.init' /etc/rc.local  
  
### Cron table setup for watchdog
$ sudo crontab -e  
$ add "* * * * * /usr/local/bin/usbcheck"  
$ add "0 * * * * /usr/local/bin/regreport"  

### Reboot
$ sudo shutdown -r now  
  
