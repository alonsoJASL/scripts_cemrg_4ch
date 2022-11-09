#!/bin/bash

scripts_path="/data/Dropbox/scripts_cemrg/fibres/atrial_fibres/"
heart_name=$1

cmd="mkdir ${heart_name}/atrial_fibres"

MESHNAME="${heart_name}/surfaces_uvc/myocardium_bayer_60_-60"
UACFOLDER="${heart_name}/atrial_fibres/UAC/"

CMD="python main_mesh.py --meshname ${MESHNAME}
						 --outdir ${UACFOLDER}
						 --raa_apex_file ./rosie_example/raa_apex.txt
						 --input_tags_setup ./parfiles/input_tags_setup_rosie.json
						 --surface endo"
eval $CMD
