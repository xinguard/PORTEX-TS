#!/usr/bin/env python2.7
import socket
import sys
import os
import threading
import RPi.GPIO as GPIO
import time

server_address = '/var/run/uds_led'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

hardware = os.popen("cat /proc/cpuinfo | grep Hardware | awk '{print $3}'"
                    ).readlines()[0].strip('\n')
if (hardware == "BCM2835"):
    GPIO.setmode(GPIO.BOARD)
    # previous bread board setup
    # YELLOW_LED_PIN = 29
    # WHITE_LED_PIN = 31
    # POWER_LED_PIN = 11
    # BLUE_LED_PIN = 13
    # RED_LED_PIN = 15
    # new circuit board setup
    YELLOW_LED_PIN = 33
    WHITE_LED_PIN = 31
    POWER_LED_PIN = 35
    BLUE_LED_PIN = 29
    RED_LED_PIN = 37
elif (hardware == "sun8iw11p1"):
    GPIO.setmode(GPIO.BOARD)
    YELLOW_LED_PIN = 29
    WHITE_LED_PIN = 31
    POWER_LED_PIN = 11
    BLUE_LED_PIN = 13
    RED_LED_PIN = 15
else:
    print "No compatible hardware found! Check /dev/cpuinfo!"
    quit()
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(WHITE_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(POWER_LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(BLUE_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RED_LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
# global variables to remember operation mode led status
# 0 off, 1 on, 2 blink
op_white = 0
op_yellow = 0
op_green = 1
op_blue = 0
op_red = 1
#global variables to control LED.
blink_green_status = False

blink_blue_status = False
blink_red_status = False
blink_blue_red_status = False

blink_white_status = False
blink_yellow_status = False
blink_admin_status = False
blink_admin3_status = False

# mode of admin_pwr.py, 0 for operation, 1 for all others
mode = 0
btmode = 0


def connection_thread(client, address):
    global blink_green_status
    global blink_blue_status
    global blink_red_status
    global blink_blue_red_status
    global blink_white_status
    global blink_yellow_status
    global blink_admin_status
    global blink_admin3_status
    global op_white, op_yellow, op_green, op_blue, op_red

    while True:
        data = client.recv(20)
        print >>sys.stderr, 'received "%s"' % data
        print type(data)
        if data:
            if data == "white_on":
                op_white = 1
                if mode == 0:
                    blink_white_status = False
                    GPIO.output(WHITE_LED_PIN, GPIO.HIGH)
            elif data == "white_off":
                op_white = 0
                if mode == 0:
                    blink_white_status = False
                    GPIO.output(WHITE_LED_PIN, GPIO.LOW)
            elif data == "white_blink":
                op_white = 2
                if mode == 0:
                    blink_white_status = True
            if data == "yellow_on":
                op_yellow = 1
                if mode == 0:
                    blink_yellow_status = False
                    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
            elif data == "yellow_off":
                op_yellow = 0
                if mode == 0:
                    blink_yellow_status = False
                    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
            elif data == "yellow_blink":
                op_yellow = 2
                if mode == 0:
                    blink_yellow_status = True
            if data == "green_on":
                op_green = 1
                if mode == 0:
                    blink_green_status = False
                    GPIO.output(POWER_LED_PIN, GPIO.HIGH)
            elif data == "green_off":
                op_green = 0
                if mode == 0:
                    blink_green_status = False
                    GPIO.output(POWER_LED_PIN, GPIO.LOW)
            elif data == "green_blink":
                op_green = 2
                if mode == 0:
                    blink_green_status = True
            if data == "blue_on":
                op_blue = 1
                if mode == 0:
                    blink_blue_status = False
                    GPIO.output(BLUE_LED_PIN, GPIO.HIGH)
            elif data == "blue_off":
                op_blue = 0
                if mode == 0:
                    blink_blue_status = False
                    GPIO.output(BLUE_LED_PIN, GPIO.LOW)
            elif data == "blue_blink":
                op_blue = 2
                if mode == 0:
                    blink_blue_status = True
            if data == "red_on":
                op_red = 1
                if mode == 0 and btmode==0:
                    blink_red_status = False
                    GPIO.output(RED_LED_PIN, GPIO.HIGH)
            elif data == "red_off":
                op_red = 0
                if mode == 0 and btmode==0:
                    blink_red_status = False
                    GPIO.output(RED_LED_PIN, GPIO.LOW)
            elif data == "red_blink":
                #op_red = 2
                if btmode == 1:
                    blink_red_status = True
            elif data == "return_to_operation":
                return_to_operation()
            elif data == "return_to_bluetooth":
                return_to_bluetooth()
            elif data == "return_to_admin":
                return_to_admin()
            elif data == "go_to_admin1":
                blink_admin_status = False
                GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
                blink_white_status = True
            elif data == "go_to_admin2":
                blink_admin_status = False
                GPIO.output(WHITE_LED_PIN, GPIO.LOW)
                blink_yellow_status = True
            elif data == "go_to_admin3":
                blink_admin_status = False
                blink_admin3_status = True
            elif data == "admin_blink_red":
                blink_red_status = True
            elif data == "admin_blink_blue":
                blink_blue_status = True
            elif data == "admin_blue_red":
                blink_blue_red_status = True
            elif data == "go_to_execute":
                blink_red_status = False
                GPIO.output(RED_LED_PIN, GPIO.LOW)
                blink_green_status = True
            elif data == "yellow_status":
                if op_yellow == 0:
                    message = "off"
                elif op_yellow == 1:
                    message = "on"
                elif op_yellow == 2:
                    message = "blink"
                else:
                    print "yellow op status error!"
                    break
                client.sendall(message)
            elif data == "white_status":
                if op_white == 0:
                    message = "off"
                elif op_white == 1:
                    message = "on"
                elif op_white == 2:
                    message = "blink"
                else:
                    print "white op status error!"
                    break
                client.sendall(message)
            elif data == "green_status":
                if op_green == 0:
                    message = "off"
                elif op_green == 1:
                    message = "on"
                elif op_green == 2:
                    message = "blink"
                else:
                    print "green op status error!"
                    break
                client.sendall(message)
            elif data == "blue_status":
                if op_blue == 0:
                    message = "off"
                elif op_blue == 1:
                    message = "on"
                elif op_blue == 2:
                    message = "blink"
                else:
                    print "blue op status error!"
                    break
                client.sendall(message)
            elif data == "red_status":
                if op_red == 2 or btmode == 1:
                    message = "blink"
                elif op_red == 1:
                    message = "on"
                elif op_red == 0:
                    message = "off"
                else:
                    print "red op status error!"
                    break
                client.sendall(message)

        else:
            break

    client.close()
    return


def startup_led():
    global blink_green_status
    blink_green_status = True
    #time.sleep(8)
    #blink_green_status = False
    #GPIO.output(POWER_LED_PIN, GPIO.HIGH)
    return


def return_to_operation():
    global blink_green_status
    global blink_blue_status
    global blink_red_status
    global blink_blue_red_status
    global blink_white_status
    global blink_yellow_status
    global blink_admin_status
    global blink_admin3_status
    global mode

    blink_green_status = False
    blink_blue_status = False
    blink_red_status = False
    blink_blue_red_status = False
    blink_white_status = False
    blink_yellow_status = False
    blink_admin_status = False
    blink_admin3_status = False
    mode = 0
    btmode = 0

    if op_green == 1:
        GPIO.output(POWER_LED_PIN, GPIO.HIGH)
    elif op_green == 2:
        blink_green_status = True
    elif op_green == 0:
        GPIO.output(POWER_LED_PIN, GPIO.LOW)

    if op_blue == 1:
        GPIO.output(BLUE_LED_PIN, GPIO.HIGH)
    elif op_blue == 2:
        blink_blue_status = True
    elif op_blue == 0:
        GPIO.output(BLUE_LED_PIN, GPIO.LOW)

    if op_red == 1:
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
    elif op_red == 2:
        blink_red_status = True
    elif op_red == 0:
        GPIO.output(RED_LED_PIN, GPIO.LOW)

    if op_white == 1:
        GPIO.output(WHITE_LED_PIN, GPIO.HIGH)
    elif op_white == 2:
        blink_white_status = True
    elif op_white == 0:
        GPIO.output(WHITE_LED_PIN, GPIO.LOW)

    if op_yellow == 1:
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
    elif op_yellow == 2:
        blink_yellow_status = True
    elif op_yellow == 0:
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

    return

def return_to_bluetooth():
    global btmode
    btmode = 1
    return



def return_to_admin():
    global blink_green_status
    global blink_blue_status
    global blink_red_status
    global blink_blue_red_status
    global blink_white_status
    global blink_yellow_status
    global blink_admin_status
    global blink_admin3_status
    global mode

    mode = 1
    blink_green_status = False
    blink_blue_status = False
    blink_red_status = False
    blink_blue_red_status = False
    blink_white_status = False
    blink_yellow_status = False
    blink_admin3_status = False
    blink_admin_status = True
    GPIO.output(POWER_LED_PIN, GPIO.LOW)
    GPIO.output(BLUE_LED_PIN, GPIO.LOW)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    return


def blink_green():
    global blink_green_status
    while True:
        if blink_green_status:
            GPIO.output(POWER_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_green_status:
            GPIO.output(POWER_LED_PIN, GPIO.LOW)
        time.sleep(1)


def blink_blue():
    while True:
        if blink_blue_status:
            GPIO.output(BLUE_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_blue_status:
            GPIO.output(BLUE_LED_PIN, GPIO.LOW)
        time.sleep(1)


def blink_red():
    while True:
        if blink_red_status:
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_red_status:
            GPIO.output(RED_LED_PIN, GPIO.LOW)
        time.sleep(1)


def blink_blue_red():
    while True:
        if blink_blue_red_status:
            GPIO.output(BLUE_LED_PIN, GPIO.HIGH)
            GPIO.output(RED_LED_PIN, GPIO.LOW)
        time.sleep(1)
        if blink_blue_red_status:
            GPIO.output(BLUE_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
        time.sleep(1)


def blink_white():
    while True:
        if blink_white_status:
            GPIO.output(WHITE_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_white_status:
            GPIO.output(WHITE_LED_PIN, GPIO.LOW)
        time.sleep(1)


def blink_yellow():
    while True:
        if blink_yellow_status:
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_yellow_status:
            GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        time.sleep(1)


def blink_admin():
    while True:
        if blink_admin_status:
            GPIO.output(WHITE_LED_PIN, GPIO.HIGH)
            GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        time.sleep(1)
        if blink_admin_status:
            GPIO.output(WHITE_LED_PIN, GPIO.LOW)
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        time.sleep(1)


def blink_admin3():
    while True:
        if blink_admin3_status:
            GPIO.output(WHITE_LED_PIN, GPIO.HIGH)
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        time.sleep(1)
        if blink_admin3_status:
            GPIO.output(WHITE_LED_PIN, GPIO.LOW)
            GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        time.sleep(1)


threading.Thread(target=blink_green).start()
threading.Thread(target=blink_blue).start()
threading.Thread(target=blink_red).start()
threading.Thread(target=blink_blue_red).start()
threading.Thread(target=blink_white).start()
threading.Thread(target=blink_yellow).start()
threading.Thread(target=blink_admin).start()
threading.Thread(target=blink_admin3).start()
threading.Thread(target=startup_led).start()


# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print >>sys.stderr, 'starting up on %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(5)

while True:
    # Wait for a connection
    connection, client_address = sock.accept()

    threading.Thread(target=connection_thread,
                     args=(connection, client_address)).start()

# Clean up the connection
connection.close()
