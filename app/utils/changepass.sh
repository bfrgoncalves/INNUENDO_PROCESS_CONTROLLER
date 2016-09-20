#!/bin/bash
newpass=$2
echo "$newpass\n$newpass\n$INNUENDO_PASS" | sudo -S passwd $1