#!/usr/bin/env bash
set -euo pipefail

mode='debug'

print_usage() {
	echo "Usage: fgcr [OPTION]"
	echo "  -h    Print this message"
	echo "  -f    Use the full dataset. If absent, uses a debug version with" \
		 " 10 samples only."
}

while getopts 'fh' flag; do
	case "${flag}" in
		f) mode='full' ;;
		h) print_usage
		   exit ;;
	esac
done

if [[ "$mode" == 'full' ]]; then
	dataset_name=relation/fgcr
else
	dataset_name=relation/fgcr-debug
fi

echo "dataset_name=${dataset_name}"

source config/data_conf/large_fgcr_conf.ini
export model_name="luyaojie/uie-base-en"
export dataset_name="${dataset_name}"
bash scripts_exp/run_exp.bash
