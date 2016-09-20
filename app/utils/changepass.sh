newpass=$2
echo -e "$INNUENDO_PASS\n$newpass\n$newpass" | sudo -S passwd $1