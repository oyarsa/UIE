#!/usr/bin/env bash
# -*- coding:utf-8 -*-

python uie_convert.py -format spotasoc -config data_config/relation/fgcr.yaml -output relation
python scripts/data_statistics.py -data converted_data/text2spotasoc/
