#!/bin/sh

if [ ! "$#" -eq 2 ]; then
	echo "$0 hostname redirect-url"
 	exit
fi

HOSTNAME=$1
REDIRECT=$2

if host -t A "${HOSTNAME}" >/dev/null 2>/dev/null ; then echo OK; else echo "Domain does not resolve"; exit; fi

echo "
server {
    listen 80;
    listen [::]:80;
    server_name $HOSTNAME;
    access_log /var/log/nginx/$HOSTNAME-access.log;
    error_log /var/log/nginx/$HOSTNAME-error.log;
    return 301 $REDIRECT;
}
" > /etc/nginx/sites-enabled/"$HOSTNAME".conf

echo "$HOSTNAME;$REDIRECT" >> /etc/nginx/redirects.csv
