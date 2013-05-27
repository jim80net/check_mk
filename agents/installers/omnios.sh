#!/bin/bash
# Written by jpark@jim80.net
# From: http://cunninghamshane.com/monitor-openindianasolaris-11-with-check_mk_agent-and-nagios/

agent=check_mk_agent.solaris


basedir=$(dirname "$0")
agentdir=${basedir}/..

agentpath=${agentdir}/${agent}

if [ "$(id -u)" != "0" ] 
then
	echo "This script must be run as root." 1>&2
	exit 1
fi

# Install mpathadm if necessary
if which mpathadm 2>&1 1> /dev/null 
then
	echo "Found mpathadm."
else
	echo "Installing mpathadm"
	pkg install mpathadm
fi

if grep -q '6556/tcp' /etc/services
then
	echo "Found check_mk definition in /etc/services"
else
	echo "Adding check_mk definition to /etc/services"
	echo "check_mk	6556/tcp" >> /etc/services
fi

if [ -f /usr/bin/check_mk_agent ] 
then
	echo "Found check_mk agent."
else
	echo "Installing check_mk agent."
	cp ${agentpath} /usr/bin/check_mk_agent
fi

if svcs check_mk/tcp:default 1> /dev/null
then 
	echo "Found service definition for check_mk"
else
	echo "Adding service defintion for check_mk"
	if [ -f /lib/svc/manifest/network/check_mk-tcp.xml ]
	then
		echo "Found service manifest. Importing."
	else
		cp ${basedir}/support_omnios/check_mk-tcp.xml /lib/svc/manifest/network/check_mk-tcp.xml
	fi
	svccfg import /lib/svc/manifest/network/check_mk-tcp.xml
	svcadm enable check_mk/tcp:default
fi

if svcs  check_mk/tcp | grep online 
then
	echo "Success!"
else
	echo "check_mk appears to be having issues. Please check."
fi
