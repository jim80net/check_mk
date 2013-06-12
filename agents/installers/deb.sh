#!/bin/bash
# Written by jpark@jim80.net
# From http://mathias-kettner.de/checkmk_linuxagent.html

agent=check_mk_agent.linux


basedir=$(dirname "$0")
agentdir=${basedir}/..

agentpath=${agentdir}/${agent}

if [ "$(id -u)" != "0" ] 
then
	echo "This script must be run as root." 1>&2
	exit 1
fi

# Install xinetd if necessary
if which xinetd 2>&1 1> /dev/null 
then
	echo "Found xinetd."
else
	echo "Installing xinetd"
	apt-get install  xinetd
fi

if which waitmax 2>&1 1> /dev/null
then
	echo "Found waitmax."
else
	echo "Installing waitmax."
	cp ${agentdir}/waitmax /usr/bin/waitmax
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

if [ -f /etc/xinetd.d/check_mk ] 
then 
	echo "Found service definition for check_mk"
else
	echo "Adding service defintion for check_mk"
	cp ${agentdir}/xinetd.conf /etc/xinetd.d/check_mk
	/etc/init.d/xinetd restart
	chkconfig xinetd on
fi

##
# Give it a sec
ping -c 1 -w 1 169.254.255.254 2>&1 1> /dev/null

if netstat -ltn | grep 6556
then
	echo "Success!"
else
	echo "check_mk appears to be having issues. Please check."
fi
