#!/usr/bin/env python2.7

import RPi.GPIO as GPIO
import time
import os
import subprocess
from threading import Thread
import socket
import sys
import syslog

# Connect the socket to the port where the server is listening
server_address = '/var/run/uds_led'

hardware = os.popen("cat /proc/cpuinfo | grep Hardware | awk '{print $3}'"
                    ).readlines()[0].strip('\n')
if (hardware == "BCM2835"):
    GPIO.setmode(GPIO.BOARD)
    # previous bread board setup
    # POWER_BUTTON_PIN = 33
    # ADMIN_BUTTON_PIN = 35
    # MCSC_BUTTON_PIN = 37
    # new circult board setup
    POWER_BUTTON_PIN = 15
    ADMIN_BUTTON_PIN = 13
    MCSC_BUTTON_PIN = 11
elif (hardware == "sun8iw11p1"):
    GPIO.setmode(GPIO.BOARD)
    POWER_BUTTON_PIN = 33
    ADMIN_BUTTON_PIN = 35
    MCSC_BUTTON_PIN = 37
else:
    print "No compatible hardware found! Check /dev/cpuinfo!"
    quit()
GPIO.setup(POWER_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ADMIN_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MCSC_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

POWEROFF_TIMER = 2
REBOOT_TIMER = 5
# global variable to distinguish between modes
# 0: operation
# 1: admin
# 2: admin1/2/3
# 3: program select
# 4: program execution
# 5: program complete
mode = 0

power_flag = 0
mcsc_flag = 0
admin_flag = 0

# variables to store operation mode white and yellow status,
# for when mcsc xor admin buttons are pressed.
op_white = 0
op_yellow = 0

CONF_PATH = "/home/portex/program_config.txt"


def send_command(message):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
    except socket.error, msg:
        print >>sys.stderr, msg
        return

    try:

        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


def power_callback(channel):
    global admin_index
    global mode
    global timer_double_counter
    global power_flag
    if mode == 0:
        time.sleep(0.5)
        pressed_time = 0.5
        while (GPIO.input(POWER_BUTTON_PIN) == GPIO.LOW):
            # while the power button is held down
            if (pressed_time >= REBOOT_TIMER):
                os.system('wall "Power button pressed for reboot...."')
                send_command("green_blink")
                # subprocess.call(['/opt/mcs/tnlctl/bin/tnlctl.sh', 'stop'], shell=False)
                # subprocess.call(['/opt/mcs/submods/proxy/scripts/ctl.sh', 'stop'], shell=False)
                print "MCS Cloud disconnect......."
                syslog.syslog(syslog.LOG_INFO, "MCS cloud disconnect.")
                os.system('shutdown -r now')
                time.sleep(100)
                return
            time.sleep(1)
            pressed_time += 1

        if (pressed_time < POWEROFF_TIMER):
            os.system('wall "Power button press cancelled."')
        else:
            os.system('wall "Power button pressed for power off..."')
            send_command("green_blink")
            # subprocess.call(['/opt/mcs/tnlctl/bin/tnlctl.sh', 'stop'], shell=False)
            # subprocess.call(['/opt/mcs/submods/proxy/scripts/ctl.sh', 'stop'], shell=False)
            print "MCS Cloud disconnect......."
            syslog.syslog(syslog.LOG_INFO, "MCS cloud disconnect.")
            os.system('shutdown -h now')
            time.sleep(100)
    elif mode == 1:
        admin_index = 1
        send_command("go_to_admin1")
        mode = 2
        timer_double_counter = 0
    elif mode == 3:
        # program select here.
        power_flag = 1

    return


def run_mcsc(type):
    # executes after mcsc button press in operation mode.
    # if config file not found, or command not found,
    # run standard command instead.
    # type = start or stop in string.
    strip_char_list = " \t\n"
    admin_index = "SI"
    if type == "start":
        program_index = "B37_1"
    elif type == "stop":
        program_index = "B37_0"
    else:
        print "run_mcsc type has to be start or stop."
        return
    file_flag = True
    command_list = []
    try:
        with open(CONF_PATH) as f:
            data = f.readlines()
    except:
        temp_string = CONF_PATH + " file"
        temp_string += " not found for run_mcsc."
        print temp_string
        syslog.syslog(syslog.LOG_WARNING, temp_string)
        file_flag = False

    if file_flag:
        for lines in data:
            words = lines.split(":")
            if admin_index == words[0].strip(strip_char_list):
                if program_index == words[1].strip(strip_char_list):
                    command_list = words[2].strip(strip_char_list).split(" ")
                    print command_list
                    break

    if not command_list:
        # run standard command here.
        if type == "start":
            # subprocess.call(['/opt/mcs/tnlctl/bin/tnlctl.sh', 'start'], shell=False)
            print "MCS Cloud connect......."
            syslog.syslog(syslog.LOG_INFO, "MCS cloud connect.")
        elif type == "stop":
            # subprocess.call(['/opt/mcs/tnlctl/bin/tnlctl.sh', 'stop'], shell=False)
            # subprocess.call(['/opt/mcs/submods/proxy/scripts/ctl.sh', 'stop'], shell=False)
            print "MCS Cloud disconnect......."
            syslog.syslog(syslog.LOG_INFO, "MCS cloud disconnect.")
    else:
        try:
            return_code = subprocess.call(command_list)
            temp_string = "Execute mcsc program " + str(command_list)
            temp_string += ", exit " + str(return_code) + "."
            syslog.syslog(syslog.LOG_INFO, temp_string)
        except:
            temp_string = 'mcsc command "' + str(command_list)
            temp_string += '" not found.'
            syslog.syslog(syslog.LOG_WARNING, temp_string)

    return


def mcsc_callback(channel):
    global admin_index
    global mode
    global timer_double_counter
    global mcsc_flag
    global op_white
    time.sleep(.1)
    if GPIO.input(MCSC_BUTTON_PIN) == GPIO.HIGH:
        print "button let go false event."
        return
    if mode == 0:
        time.sleep(.5)
        if (
            GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW and
            GPIO.input(MCSC_BUTTON_PIN) == GPIO.LOW
        ):
            # admin and mcsc both held down after 1 second
            print "mcsc operation mode mcsc+admin held down."
            return

        if op_white == 1:
            send_command("white_off")
            op_white = 0
            # time.sleep(3)
            run_mcsc("stop")
        else:
            send_command("white_on")
            op_white = 1
            # time.sleep(2)
            run_mcsc("start")
    elif mode == 1:
        time.sleep(.5)
        if (
            GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW and
            GPIO.input(MCSC_BUTTON_PIN) == GPIO.LOW
        ):
            # admin and mcsc both held down after 1 second
            print "mcsc admin mode mcsc+admin held down."
            return

        admin_index = 2
        send_command("go_to_admin2")
        mode = 2
        timer_double_counter = 0
    elif mode == 3:
        # program select here.
        mcsc_flag = 1

    return


def return_to_operation():
    send_command("return_to_operation")
    syslog.syslog(syslog.LOG_INFO, 'Return to operation mode.')
    return


def return_to_admin():
    global timer_double_counter
    global admin_flag
    global mcsc_flag
    global power_flag

    timer_double_counter = 0
    admin_flag = 0
    mcsc_flag = 0
    power_flag = 0
    send_command("return_to_admin")
    return


def run_program():
    global mode
    time.sleep(6)
    total_program_index = admin_flag + (mcsc_flag << 1) + (power_flag << 2)
    print "admin index: ", admin_index
    print "program index: ", total_program_index
    send_command("go_to_execute")
    time.sleep(2)
    read_and_run(str(admin_index), str(total_program_index))
    print "program output here."
    time.sleep(6)
    mode = 1
    return_to_admin()
    return


def read_and_run(admin_index, program_index):
    # results and their color displays:
    # blink blue: return code 0 only
    # blink red: return code others
    # blink blud_red: all exceptions, and index not found.
    strip_char_list = " \t\n"

    temp_string = "admin index: " + admin_index
    temp_string += ", program index: " + program_index
    print temp_string
    try:
        with open(CONF_PATH) as f:
            data = f.readlines()
    except:
        temp_string = CONF_PATH + " file"
        temp_string += " not found."
        print temp_string
        syslog.syslog(syslog.LOG_WARNING, temp_string)
        send_command("admin_blue_red")
        return

    for lines in data:
        words = lines.split(":")
        if admin_index == words[0].strip(strip_char_list):
            if program_index == words[1].strip(strip_char_list):
                command = words[2].strip(strip_char_list).split(" ")
                print command
                try:
                    return_code = subprocess.call(command)
                    temp_string = "execute program " + admin_index
                    temp_string += "/" + program_index + ", exit "
                    temp_string += str(return_code) + "."
                    syslog.syslog(syslog.LOG_INFO, temp_string)
                    if return_code == 0:
                        send_command("admin_blink_blue")
                    else:
                        send_command("admin_blink_red")
                except:
                    print "cannot execute."
                    temp_string = 'command "' + str(command)
                    temp_string += '" not found.'
                    syslog.syslog(syslog.LOG_WARNING, temp_string)
                    send_command("admin_blue_red")
                finally:
                    return

    # admin/program index not found.
    temp_string = "program " + admin_index + "/" + program_index
    temp_string += " not found."
    print temp_string
    syslog.syslog(syslog.LOG_WARNING, temp_string)
    send_command("admin_blue_red")
    return


def run_admin(type):
    # executes after admin button press in operation mode.
    # if config file not found, or command not found,
    # run standard command instead.
    # type = start or stop in string.
    strip_char_list = " \t\n"
    admin_index = "SI"
    if type == "start":
        program_index = "B35_1"
    elif type == "stop":
        program_index = "B35_0"
    else:
        print "run_admin type has to be start or stop."
        return
    file_flag = True
    command_list = []
    try:
        with open(CONF_PATH) as f:
            data = f.readlines()
    except:
        temp_string = CONF_PATH + " file"
        temp_string += " not found for run_admin."
        print temp_string
        syslog.syslog(syslog.LOG_WARNING, temp_string)
        file_flag = False

    if file_flag:
        for lines in data:
            words = lines.split(":")
            if admin_index == words[0].strip(strip_char_list):
                if program_index == words[1].strip(strip_char_list):
                    command_list = words[2].strip(strip_char_list).split(" ")
                    print command_list
                    break

    if not command_list:
        # run standard command here.
        print type
        if type == "start":
            # subprocess.call(['python', '/opt/mcs/cbox_panel_control/bin/led_bt_server.py'],
            #                shell=False)
            # os.system('service bluetooth start')
            # os.system('/opt/mcs/cbox_panel_control/bin/led_bt_server.py > /dev/null &')
            print "Bluetooth console enable"
            syslog.syslog(syslog.LOG_INFO, "Bluetooth console enable.")
        elif type == "stop":
            # subprocess.call(['ps -ef | grep led_bt_server | grep -v grep |awk \'{print "kill "$2}\' | bash'], shell=True)
            # os.system('service bluetooth stop')
            send_command("return_to_operation")
            print "Bluetooth console disable"
            syslog.syslog(syslog.LOG_INFO, "Bluetooth console disable.")
    else:
        try:
            return_code = subprocess.call(command_list)
            temp_string = "Execute admin program " + str(command_list)
            temp_string += ", exit " + str(return_code) + "."
            syslog.syslog(syslog.LOG_INFO, temp_string)
        except:
            temp_string = 'admin command "' + str(command_list)
            temp_string += '" not found.'
            syslog.syslog(syslog.LOG_WARNING, temp_string)

    return


GPIO.add_event_detect(POWER_BUTTON_PIN, GPIO.FALLING, callback=power_callback,
                      bouncetime=1000)
GPIO.add_event_detect(MCSC_BUTTON_PIN, GPIO.FALLING, callback=mcsc_callback,
                      bouncetime=1000)
try:
    while True:
        while (GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW):
            time.sleep(1)

        ch = GPIO.wait_for_edge(ADMIN_BUTTON_PIN, GPIO.FALLING,
                                timeout=6000)

        #print "Falling edge detected."
        if (mode == 0):
            # operation mode
            if ch is None:
                continue
            time.sleep(0.5)
            if (
                GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW and
                GPIO.input(MCSC_BUTTON_PIN) == GPIO.LOW
            ):
                # admin and mcsc both held down after 1 second,
                # enter admin mode
                print "admin mode activated."
                syslog.syslog(syslog.LOG_INFO, 'Start admin mode.')
                mode = 1
                return_to_admin()
                continue

            if op_yellow == 1:
                print "yellow_off"
                send_command("yellow_off")
                op_yellow = 0
                # time.sleep(3)
                run_admin("stop")
            else:
                print "yellow on"
                send_command("yellow_on")
                op_yellow = 1
                # time.sleep(2)
                run_admin("start")
        elif (mode == 1):
            if ch is None:
                if timer_double_counter > 2:
                    print "admin timeout in admin mode."
                    return_to_operation()
                    mode = 0
                    continue
                else:
                    timer_double_counter += 1
                    continue
            time.sleep(0.5)
            if (
                GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW and
                GPIO.input(MCSC_BUTTON_PIN) == GPIO.LOW
            ):
                print "Returning to operation mode from admin."
                return_to_operation()
                mode = 0
                continue

            # if here, go to admin3
            admin_index = 3
            send_command("go_to_admin3")
            mode = 2
            timer_double_counter = 0
        elif mode == 2:
            if ch is None:
                if timer_double_counter > 2:
                    print "admin timeout in admin1/2/3 mode."
                    return_to_operation()
                    mode = 0
                    continue
                else:
                    timer_double_counter += 1
                    continue
            time.sleep(0.5)
            if (
                GPIO.input(ADMIN_BUTTON_PIN) == GPIO.LOW and
                GPIO.input(MCSC_BUTTON_PIN) == GPIO.LOW
            ):
                print "Returning to operation mode from admin3."
                return_to_operation()
                mode = 0
                continue

            # admin1/2/3 start.
            mode = 3
            send_command("admin_blink_red")
            run_program_process = Thread(target=run_program)
            run_program_process.start()
        elif mode == 3:
            # program select here.
            admin_flag = 1

except KeyboardInterrupt:
    print "interrupted."
