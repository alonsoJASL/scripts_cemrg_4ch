#!/bin/bash

MESHNAME="./example_01/01_fch"
UACFOLDER="./example_01/UAC/"

CMD="python main_mesh.py --meshname ${MESHNAME}
						 --outdir ${UACFOLDER}
						 --raa_apex_file ./example_01/raa_apex.txt"
eval $CMD
