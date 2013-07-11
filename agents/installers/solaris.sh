#!/bin/bash
# Written by jpark@jim80.net
# From: http://cunninghamshane.com/monitor-openindianasolaris-11-with-check_mk_agent-and-nagios/

agent=check_mk_agent.solaris

if [ "$1" = "force" ] 
then
	FORCE=1
else
	FORCE=0
fi

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
				DESTPATH="/usr/bin"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.omnios
				DESTMANIFEST=/lib/svc/manifest/network/check_mk-tcp.xml
				DESTLIBDIR=/opt/local/lib/check_mk_agent
				DESTCONFDIR=/opt/local/etc/check_mk
				;;
			joyent*) 
				UNAME=smartos
				EXECUTABLES="mpathadm"
				PKGINSTALL="pkgin in"
				DESTPATH="/opt/custom/bin"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.smartos
				DESTMANIFEST=/opt/custom/smf/check_mk-tcp.xml
				DESTLIBDIR=/opt/custom/lib/check_mk_agent
				DESTCONFDIR=/opt/custom/etc/check_mk
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
				DESTPATH="/opt/local/bin"
				SOURCEMANIFEST=${basedir}/support_solaris/check_mk-tcp.xml.smartoszone
				DESTMANIFEST=/var/svc/manifest/network/check_mk-tcp.xml
				DESTLIBDIR=/opt/local/lib/check_mk_agent
				DESTCONFDIR=/opt/local/etc/check_mk
				;;
			*) UNAME=undef
				echo "Unable to identify solaris version. Quitting."
				exit 1
				;;
		esac
		;;
esac

if [ ! -d ${DESTLIBDIR} ] 
then
	mkdir -p ${DESTLIBDIR}
fi

if [ ! -d ${DESTCONFDIR} ] 
then
	mkdir -p ${DESTCONFDIR}
fi


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

if [ -f ${DESTPATH}/check_mk_agent ] && [ $FORCE -ne 1 ] 
then
	echo "Found check_mk agent."
else
	echo "Installing check_mk agent."
	mkdir -p ${DESTPATH}
	cat ${agentpath} | sed -e "s:export MK_LIBDIR=.*$:export MK_LIBDIR=${DESTLIBDIR}:" | sed -e "s:export MK_CONFDIR=.*$:export MK_CONFDIR=${DESTCONFDIR}:" > ${DESTPATH}
  	chmod +x ${DESTPATH}
fi

if svcs check_mk/tcp:default 1> /dev/null 
then 
	FOUNDSVC=1
  ADDSVC=0
else
	FOUNDSVC=0
	ADDSVC=1
fi

if [ $FOUNDSVC  -eq 1 ] && [ $FORCE -ne 1 ] 
then
	echo "Found service definition for check_mk"
elif [ $FOUNDSVC -eq 1 ] && [ $FORCE -eq 1 ] 
then
  svcadm disable check_mk/tcp:default
  svccfg delete check_mk/tcp:default
  ADDSVC=1
fi
	
if [ $ADDSVC -eq 1 ] 
then
	echo "Adding service defintion for check_mk"
	cp ${SOURCEMANIFEST} ${DESTMANIFEST}
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
