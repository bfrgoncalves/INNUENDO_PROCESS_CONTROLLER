#!/bin/bash
echo $INNUENDO_PASS | sudo -S useradd -m $1 -g ftpaccess -s /usr/sbin/nologin
#echo $INNUENDO_PASS | sudo -S passwd $1
newpass=$3
echo "$newpass\n$newpass\n$INNUENDO_PASS" | sudo -S passwd $1
echo $INNUENDO_PASS | sudo -S chown root /home/$1
echo $INNUENDO_PASS | sudo -S mkdir /home/$1/$2
echo $INNUENDO_PASS | sudo -S chown $1:ftpaccess /home/$1/$2

