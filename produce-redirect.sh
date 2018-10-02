#!/bin/sh

if [ ! "$#" -eq 2 ]; then
	echo "$0 hostname redirect-url"
 	exit
fi

HOSTNAME=$1
REDIRECT=$2

if host -t A ${HOSTNAME} >/dev/null 2>/dev/null ; then echo OK; else echo "Domain does not resolve"; exit; fi

echo "
server {
    listen 80;
    listen [::]:80;
    server_name $1;
    access_log /var/log/nginx/$1-access.log;
    error_log /var/log/nginx/$1-error.log;
    return 301 $2;
}
" > /etc/nginx/sites-enabled/$1.conf

echo "$1;$2" >> /etc/nginx/redirects.csv
