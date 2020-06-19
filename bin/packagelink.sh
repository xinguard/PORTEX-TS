#!/bin/bash

for FILE in `ls | awk '{print $NF}'`; do
	[ -f /usr/local/bin/$FILE ] && rm /usr/local/bin/$FILE
	ln -s ~pi/usrlocalbin/$FILE /usr/local/bin/$FILE
done


