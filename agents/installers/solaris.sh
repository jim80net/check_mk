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

# Find out what zone we are running in
# Treat all pre-Solaris 10 systems as "global"
if type zonename &>/dev/null
then
    zonename=$(zonename)
    pszone="-z $zonename"
else
    zonename="global"
    pszone="-A"
fi

case $zonename in
	global)
		UNAMEV=$(uname -v)
		case $UNAMEV in
			omnios*) 
				UNAME=omnios
				EXECUTABLES="mpathadm"
				PKGINSTALL="pkg install"
				DESTPATH="/usr/bin/check_mk_agent"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.omnios
				DESTMANIFEST=/lib/svc/manifest/network/check_mk-tcp.xml
				;;
			joyent*) 
				UNAME=smartos
				EXECUTABLES="mpathadm"
				PKGINSTALL="pkgin in"
				DESTPATH="/opt/custom/bin/check_mk_agent"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.smartos
				DESTMANIFEST=/opt/custom/smf/check_mk-tcp.xml
				;;
			*) UNAME=undef
				echo "Unable to identify solaris version. Quitting."
				exit 1
				;;
		esac
		;;
	*)
		UNAMEV=$(uname -v)
		case $UNAMEV in
			joyent*) 
				UNAME=smartos
				EXECUTABLES="mpathadm"
				PKGINSTALL="pkgin in"
				DESTPATH="/opt/local/bin/check_mk_agent"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.smartoszone
				DESTMANIFEST=/var/svc/manifest/network/check_mk-tcp.xml
				;;
			*) UNAME=undef
				echo "Unable to identify solaris version. Quitting."
				exit 1
				;;
		esac
		;;
esac

# Install EXECUTABLES
if [ "${EXECUTABLES}" != "" ] 
then
	for each in ${EXECUTABLES}
	do
		if which ${each} 2>&1 1> /dev/null 
		then
			echo "Found ${each}."
		else
			echo "Installing ${each}"
			${PKGINSTALL} ${each}
		fi
	done
fi

if grep -q '6556/tcp' /etc/services
then
	echo "Found check_mk definition in /etc/services"
else
	echo "Adding check_mk definition to /etc/services"
	echo "check_mk	6556/tcp" >> /etc/services
fi

if [ -f ${DESTPATH} ]
then
	echo "Found check_mk agent."
else
	echo "Installing check_mk agent."
	cp ${agentpath} ${DESTPATH}
fi

if svcs check_mk/tcp:default 1> /dev/null
then 
	echo "Found service definition for check_mk"
else
	echo "Adding service defintion for check_mk"
	if [ -f ${DESTMANIFEST} ] 
	then
		echo "Found service manifest. Importing."
	else
		cp ${SOURCEMANIFEST} ${DESTMANIFEST}
	fi
	svccfg import ${DESTMANIFEST}
	svcadm enable check_mk/tcp:default
fi

# give it a sec
sleep 1

if svcs  check_mk/tcp | grep online 
then
	echo "Success!"
else
	echo "check_mk appears to be having issues. Please check."
fi
