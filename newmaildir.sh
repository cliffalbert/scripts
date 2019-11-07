#!/bin/sh
MONTH=`date +%Y/%m`
YEAR=`date +%Y`
mkdir -p $HOME/mail/$MONTH
ln -sf $HOME/mail/ $HOME/mail/$MONTH/archived-mail
if [ -e $HOME/mail/current ]; then
 rm $HOME/mail/current
 ln -sf $HOME/mail/$MONTH $HOME/mail/current
fi
