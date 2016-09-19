#!/bin/bash
echo $INNUENDO_PASS | sudo -S useradd -m $1 -g ftpaccess -s /usr/sbin/nologin
