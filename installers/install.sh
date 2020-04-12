#!/bin/bash
# -----------------------------------------------------------------------------
# [Ravin A.] Gitlab helper telegram bot installer
#            Installs service
# -----------------------------------------------------------------------------

VERSION=0.0.1
TITLE=gitlab_helper_installer
SUBJECT=$TITLE-$VERSION-process
CURRENT_DIR="$(dirname "$0")"

# --- Make sure only root can run our script ----------------------------------
if [[ $EUID -ne 0 ]]; then
	print_error "This script must be run as root!"
	exit 1
fi

# --- Locks -------------------------------------------------------------------
LOCK_FILE=/tmp/$SUBJECT.lock
if [ -f "$LOCK_FILE" ]; then
   echo "Script is already running"
   exit
fi

trap "rm -f $LOCK_FILE" EXIT
touch $LOCK_FILE

# --- Basic functions ---------------------------------------------------------
RED='\033[0;31m'
Yellow='\033[1;33m'
Green='\033[0;32m'
NC='\033[0m' # No Color

# print FAIL or OK in case of work result
print_result ()
{
	if [ $? -eq 0 ]; then
		echo -n -e "$(tput hpa $(tput cols))$(tput cub 6)${Green}[OK]${NC}"
		echo
	else
		echo -n -e "$(tput hpa $(tput cols))$(tput cub 6)${RED}[fail]${NC}"
		echo
	fi
}

# Prints progress status in top of the windows
print_status ()
{
	local arg="$1"
	local cols=$(tput cols)
	local second_max_len=$(((cols - ${#arg}) / 2 - 2))
	if ((${#arg} % 2)); then
		arg="${arg} "
	fi
	local line_first=""
	local line_second=""

	for (( iter=0; iter < $cols; iter++ )); do
		line_first="${line_first}_"
		if ! ((iter % 2)); then
			if [ "${#line_second}" -le "$second_max_len" ]; then
				line_second="${line_second}-"
			fi
		fi
	done

	echo -e "${Yellow}${line_first}${NC}"
	echo -e "${Yellow}${line_second} ${RED}${arg}${Yellow} ${line_second}${NC}"
}

# Prints a error message to console
print_error ()
{
	echo -e "${RED}$1${NC}"
}

# --- Body --------------------------------------------------------------------
# Redirect output to file
LOG_FILE="$CURRENT_DIR/install.log"
exec &> >(tee -a $LOG_FILE)
clear
> $LOG_FILE

print_status "Starting gitlab_helper service"
cat gitlab_helper.service | tr -d '\r' > /etc/systemd/system/gitlab_helper.service
chmod 664 /etc/systemd/system/gitlab_helper.service
systemctl daemon-reload
systemctl start gitlab_helper.service
systemctl enable gitlab_helper
print_result

# -----------------------------------------------------------------------------