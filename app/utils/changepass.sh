newpass=$2
echo $newpass
echo $INNUENDO_PASS
echo 'in1 ' $1
echo 'in2 ' $2
echo -e "$newpass\n$newpass\n$INNUENDO_PASS"
echo -e "$newpass\n$newpass\n$INNUENDO_PASS" | sudo -S passwd $1