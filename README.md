# PORTEX-TS

## Terminal server on Raspberry Pi
## Use Raspberry Pi as a small terminal server
## Support local account/password and TACACS+ authentication

## PORTEX-TS software package installation guide

### System package upgrade:
$ sudo apt update  
$ sudo apt dist-upgrade  
$ sudo apt -y install python-pip  
$ sudo pip install --upgrade pip  

### Necessary package installation:
$ sudo apt -y install dialog git minicom tmux whois ntpdate   
$ sudo pip install tacacs_plus RPi.GPIO   

### PORTEX-TS program installation
$ cd /tmp  
$ git clone https://github.com/xinguard/PORTEX-TS.git  
$ cd PORTEX-TS  
$ sudo /bin/bash setup.sh  

### Reboot if program prompt
$ sudo shutdown -r now  
  
