#!/usr/bin/env bash
set -euxo pipefail

source config/data_conf/large_conll04_conf.ini
export model_name="luyaojie/uie-base-en"
export dataset_name=relation/fgcr
bash scripts_exp/run_exp.bash
