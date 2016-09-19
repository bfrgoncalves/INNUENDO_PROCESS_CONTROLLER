#!/bin/bash
echo $INNUENDO_PASS | sudo -S useradd -m $1 -g ftpaccess -s /usr/sbin/nologin
#echo $INNUENDO_PASS | sudo -S passwd $1
echo $INNUENDO_PASS | sudo -S chown root /home/$1
echo $INNUENDO_PASS | sudo -S mkdir /home/data/INNUENDO
echo $INNUENDO_PASS | sudo -S chown john:ftpaccess /home/$1/INNUENDO

