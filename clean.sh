#!/usr/bin/env sh
#
# Remove all the .pyc and .pyo files from the root directory of the project
# and all its subdirectories
#

if [[ $# -lt 1 || $# -gt 1 ]]; then
	echo ""
	echo "Usage: $0 root_directory"
	echo ""
	echo "This script remove all .pyc and .pyo files from root_directory"
	echo "and all the directories under <root_folder>"
else

	if [ -d $1 ]; then
		echo ""
		echo "### Removing *.pyc and *.pyo files ###"
		echo ""
		rm -vf *.pyc
		rm -vf *.pyo

		for entry in $1/*; do
			# Remove pyc and pyo files from the directory
			if [[ -d $entry && $entry != .. ]]; then
				echo "+++ Entering subidrectory $entry"
				cd $entry
				rm -vf *.pyc
				rm -vf *.pyo
				cd ..
				echo "--- Leaving subdirectory $entry"
			fi
		done

		echo "--- Finished"
	else
		echo "'$1' is not a directory"
	fi
fi