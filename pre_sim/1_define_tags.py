import os
import numpy as np
from SIMULATION_library import mesh_utils
import json
import argparse

parser = argparse.ArgumentParser(description='To run: python3 define_tags.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

MESHFOLDER=HEART_FOLDER+"pre_simulation/"

os.system("mkdir "+MESHFOLDER)
os.system("cp "+HEART_FOLDER+"/atrial_fibres/myocardium_fibres_l.elem "+MESHFOLDER+"/myocardium.elem")
os.system("cp "+HEART_FOLDER+"/atrial_fibres/myocardium_fibres_l.pts "+MESHFOLDER+"/myocardium.pts")
os.system("cp "+HEART_FOLDER+"/atrial_fibres/myocardium_fibres_l.lon "+MESHFOLDER+"/myocardium.lon")

MESHNAME="myocardium"
MESHNAME_AV="myocardium_AV"
MESHNAME_FEC="myocardium_AV_FEC"
MESHNAME_BB="myocardium_AV_FEC_BB"

json_tags = "./tags.json"
json_settings = "./bachmann_bundle_fec_settings.json"

f_input = open(json_tags,"r")
tags = json.load(f_input)
f_input.close()

f_input = open(json_settings,"r")
settings = json.load(f_input)
f_input.close()

###############################################
# 0 AV plane - extract biv mesh with meshtool 
# give the path
###############################################

if not os.path.exists(MESHFOLDER+"/"+MESHNAME_AV+".elem"):
	mesh_utils.define_AV_separation(MESHFOLDER+"/"+MESHNAME+".elem",
				  		 			tags,
				  		 			27,
				  		 			MESHFOLDER+"/"+MESHNAME_AV+".elem")

###########################################
# 1 FEC- extract biv mesh with meshtool 
# give the path
###########################################

BIVFOLDER=HEART_FOLDER+"/surfaces_uvc/BiV"
BIVMESHNAME=BIVFOLDER+"/BiV"
Zbiv_file=BIVFOLDER+"/uvc/BiV.uvc_z.dat"
RHObiv_file=BIVFOLDER+"/uvc/BiV.uvc_rho.dat"

if not os.path.exists(MESHFOLDER+"/"+MESHNAME_FEC+".elem"):
	mesh_utils.define_FEC(MESHFOLDER+"/"+MESHNAME_AV+".elem",
						  BIVMESHNAME,
						  Zbiv_file,
						  RHObiv_file,
						  MESHFOLDER+"/"+MESHNAME_FEC+".elem",
						  tags["fast_endo"],
						  include_septum=BIVFOLDER+"/BiV.rvsept.surf",
						  FEC_height=settings["FEC_height"])

###########################################
# 2 BB - extract la and ra submeshes
###########################################
LAfolder=HEART_FOLDER+"/surfaces_uvc_LA/la/"
LAMESHNAME=LAfolder+"/la"
RAfolder=HEART_FOLDER+"/surfaces_uvc_RA/ra/"
RAMESHNAME=RAfolder+"/ra"
Zla_file=LAfolder+"uvc/la.uvc_z.dat"
Zra_file=RAfolder+"uvc/ra.uvc_z.dat"
PHIla_file=LAfolder+"uvc/la.uvc_phi.dat"
PHIra_file=RAfolder+"uvc/ra.uvc_phi.dat"

if not os.path.exists(MESHFOLDER+"/"+MESHNAME_BB+".elem"):
	mesh_utils.define_BB(MESHFOLDER+"/"+MESHNAME_FEC+".elem",
						 LAMESHNAME,
						 RAMESHNAME,
						 Zla_file,
						 Zra_file,
						 PHIla_file,
						 PHIra_file,
						 settings,
						 tags,
						 MESHFOLDER+"/"+MESHNAME_BB+".elem")

	os.system("cp  "+MESHFOLDER+"/"+MESHNAME+".pts "+MESHFOLDER+"/"+MESHNAME_BB+".pts")
	os.system("cp  "+MESHFOLDER+"/"+MESHNAME+".lon "+MESHFOLDER+"/"+MESHNAME_BB+".lon")
	os.system("meshtool convert -imsh="+MESHFOLDER+"/"+MESHNAME_BB+" -omsh="+MESHFOLDER+"/"+MESHNAME_BB+".vtk")
	# os.system("rm  "+MESHFOLDER+"/"+MESHNAME_BB+".pts")
	# os.system("rm  "+MESHFOLDER+"/"+MESHNAME_BB+".lon")