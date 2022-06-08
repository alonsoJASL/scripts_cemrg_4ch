# generate valve planes

# how to call from Seg3D bin directory:

"""
exec(open('/data/Dropbox/scripts/Seg/py/generateValvePlanes_optimised.py').read())
"""

#import sys

#from joblib import delayed, Parallel
#import itertools
#import math
#import multiprocessing
#import nrrd
#import numpy
import os
import subprocess
import time
import json

filepath = "/data/Dropbox/henry/segmentations/"
filenames = "seg_s3b.nrrd"

NpulmVeins = 4

InitialSegmentation = importlayer(filename=filepath + '/' + filenames,importer='[Teem Importer]',mode='data',inputfiles_id=5)

# The layers must have this exact numbering... 

#ID_Back   = threshold(layerid=InitialSegmentation[0],lower_threshold=0.00,upper_threshold=0.00) # background          
ID_LV_BP = threshold(layerid=InitialSegmentation[0],lower_threshold=1.00,upper_threshold=1.00) # LV Blood pool
ID_LV_Myo_new = threshold(layerid=InitialSegmentation[0],lower_threshold=2.00,upper_threshold=2.00) # LV myocardium       
ID_RV_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=3.00,upper_threshold=3.00) # RV blood pool
ID_RV_Myo  = threshold(layerid=InitialSegmentation[0],lower_threshold=4.00,upper_threshold=4.00) # myocardium
ID_LA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=5.00,upper_threshold=5.00) # LA blood pool
ID_LA_Myo  = threshold(layerid=InitialSegmentation[0],lower_threshold=6.00,upper_threshold=6.00) # LA myocardium
ID_RA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=7.00,upper_threshold=7.00) # RA blood pool
ID_RA_Myo  = threshold(layerid=InitialSegmentation[0],lower_threshold=8.00,upper_threshold=8.00) # RA myocardium
ID_Ao_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=9.00,upper_threshold=9.00) # Aorta blood pool
ID_Ao_WT  = threshold(layerid=InitialSegmentation[0],lower_threshold=10.00,upper_threshold=10.00) # Aorta wall thickness
ID_PArt_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=11.00,upper_threshold=11.00) # Pulm artery blood pool
ID_PArt_WT  = threshold(layerid=InitialSegmentation[0],lower_threshold=12.00,upper_threshold=12.00) # Pulm artery wall thickness
ID_LPVeins_BP_1  = threshold(layerid=InitialSegmentation[0],lower_threshold=13.00,upper_threshold=13.00) # Left pulmonary 1 vein blood pool    
ID_LPVeins_BP_2  = threshold(layerid=InitialSegmentation[0],lower_threshold=14.00,upper_threshold=14.00) # Left pulmonary 2 vein blood pool  
ID_LAA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=15.00,upper_threshold=15.00) # Left atrial appendage blood pool
ID_RPVeins_BP_1  = threshold(layerid=InitialSegmentation[0],lower_threshold=16.00,upper_threshold=16.00) # Right pulmonary 1 vein blood pool    
ID_RPVeins_BP_2  = threshold(layerid=InitialSegmentation[0],lower_threshold=17.00,upper_threshold=17.00) # Right pulmonary 2 vein blood pool    
ID_SVC_BP = threshold(layerid=InitialSegmentation[0],lower_threshold=18.00,upper_threshold=18.00) # SVC blood pool    
ID_IVC_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=19.00,upper_threshold=19.00) # IVC blood pool
time.sleep(4)
deletelayers(layers = InitialSegmentation) 

time.sleep(6)

valve_WT = 2.5
LA_WT = 2.00
RA_WT = 2.00

file = open('/data/Dropbox/Segmentations/2016111001EP/py/points.json')
data_main = json.load(file)

file = open('/data/Dropbox/Segmentations/2016111001EP/py/gVP_points.json')
data_gVP = json.load(file)

LV_BP_seed = [data_main['LV_BP']]

Ao_BP_seed = [data_main['aorta']]
Ao_WT_seed = [data_gVP['Ao_WT']]

RV_BP_seed = [data_main['RV_BP']]
RV_Myo_seed = [data_gVP['RV_Myo']]

PA_BP_seed = [data_main['pulm_art']]
PA_WT_seed = [data_gVP['PA_WT']]

LA_BP_seed = [data_main['LA_BP']]
LA_Myo_seed = [data_gVP['LA_Myo']]

RA_BP_seed = [data_main['RA_BP']]
RA_Myo_seed = [data_gVP['RA_Myo']]

# --------------------------------------------------------------------------------------------------
# Generate valve planes - Mitral valve
# --------------------------------------------------------------------------------------------------

ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_MV_temp = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_MV_temp = andfilter(layerid=ID_MV_temp,mask=ID_LV_BP,replace='true')
time.sleep(6)

ID_LV_BP = removefilter(layerid=ID_LV_BP,mask=ID_MV_temp,replace='true')
time.sleep(6)

deletelayers(layers=[ID_distMap])

ID_distMap = distancefilter(layerid=ID_LV_Myo_new)
time.sleep(5)

ID_LV_Myo_extra = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=2.00)
time.sleep(6)

ID_LA_Myo_extra = andfilter(layerid=ID_LV_Myo_extra,mask=ID_LA_BP,replace='true')
time.sleep(6)
ID_LA_Myo = orfilter(layerid=ID_LA_Myo_extra,mask=ID_LA_Myo,replace='true')
time.sleep(6)

# --------------------------------------------------------------------------------------------------
# Generate valve planes - Tricuspid valve
# --------------------------------------------------------------------------------------------------

ID_distMap = distancefilter(layerid=ID_RA_BP)
time.sleep(5)

ID_TV_temp = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_TV_temp = andfilter(layerid=ID_TV_temp,mask=ID_RV_BP,replace='true')
time.sleep(6)

ID_RV_BP = removefilter(layerid=ID_RV_BP,mask=ID_TV_temp,replace='true')
time.sleep(6)

deletelayers(layers=[ID_distMap])

ID_distMap = distancefilter(layerid=ID_RV_Myo)
time.sleep(6)

ID_RV_Myo_extra = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=2.00)
time.sleep(6)

ID_RA_Myo_extra = andfilter(layerid=ID_RV_Myo_extra,mask=ID_RA_BP,replace='true')
time.sleep(6)
ID_RA_Myo = orfilter(layerid=ID_RA_Myo_extra,mask=ID_RA_Myo,replace='true')
time.sleep(6)

# --------------------------------------------------------------------------------------------------
# Generate valve planes - Aortic valve
# --------------------------------------------------------------------------------------------------

ID_distMap = distancefilter(layerid=ID_Ao_BP)
time.sleep(5)

ID_AV_temp = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_AV_temp = andfilter(layerid=ID_AV_temp,mask=ID_LV_BP,replace='true')
time.sleep(6)

ID_LV_BP = removefilter(layerid=ID_LV_BP,mask=ID_AV_temp,replace='true')
time.sleep(6)

deletelayers(layers=[ID_distMap])

ID_distMap = distancefilter(layerid=ID_Ao_WT)
time.sleep(6)

ID_Ao_WT_extra = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=2.00)
time.sleep(6)

ID_LV_Myo_extra = andfilter(layerid=ID_Ao_WT_extra,mask=ID_LV_BP,replace='true')
time.sleep(6)
ID_LV_Myo = orfilter(layerid=ID_LV_Myo_extra,mask=ID_LV_Myo_new,replace='true')
time.sleep(6)

# --------------------------------------------------------------------------------------------------
# Generate valve planes - Pulmonary valve
# --------------------------------------------------------------------------------------------------

ID_distMap = distancefilter(layerid=ID_PArt_BP)
time.sleep(5)

ID_PV_temp = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_PV_temp = andfilter(layerid=ID_PV_temp,mask=ID_RV_BP,replace='true')
time.sleep(6)

ID_RV_BP = removefilter(layerid=ID_RV_BP,mask=ID_PV_temp,replace='true')
time.sleep(6)

deletelayers(layers=[ID_distMap])

ID_distMap = distancefilter(layerid=ID_RV_Myo)
time.sleep(6)

ID_RV_Myo_extra = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=2.00)
time.sleep(6)

ID_PArt_WT_extra = andfilter(layerid=ID_RV_Myo_extra,mask=ID_PArt_BP,replace='true')
time.sleep(6)
ID_PArt_WT_new = orfilter(layerid=ID_PArt_WT,mask=ID_PArt_WT_extra,replace='true')
time.sleep(6)

ID_distMap = distancefilter(layerid=ID_PArt_WT)
time.sleep(6)

ID_PArt_WT_extra = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=2.00)
time.sleep(6)

ID_PArt_WT_extra = andfilter(layerid=ID_PArt_WT_extra,mask=ID_RV_BP,replace='true')
time.sleep(6)
ID_RV_Myo = orfilter(layerid=ID_RV_Myo,mask=ID_RV_Myo_extra,replace='true')
time.sleep(6)
ID_RV_Myo = orfilter(layerid=ID_RV_Myo,mask=ID_PArt_WT_extra,replace='true')
time.sleep(6)

# ------------------------------------------------------------------------------------------------
# Generate rings for pulmonary veins, LAA, SVC and IVC
# ------------------------------------------------------------------------------------------------

ring_thickness=4.00		# threshold used on distance filter to generate rings

# Left pulmonary vein #1
ID_distMap = distancefilter(layerid=ID_LPVeins_BP_1)
time.sleep(6)
ID_LPVeins_ring_1 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_LPVeins_ring_1 = removefilter(layerid=ID_LPVeins_ring_1,mask=ID_LA_BP,replace=True)
time.sleep(6)
ID_LPVeins_ring_1 = removefilter(layerid=ID_LPVeins_ring_1,mask=ID_LA_Myo,replace=True)
time.sleep(6)
ID_LPVeins_ring_1 = removefilter(layerid=ID_LPVeins_ring_1,mask=ID_LPVeins_BP_1,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# Left pulmonary vein #2
ID_distMap = distancefilter(layerid=ID_LPVeins_BP_2)
time.sleep(6)
ID_LPVeins_ring_2 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_LPVeins_ring_2 = removefilter(layerid=ID_LPVeins_ring_2,mask=ID_LA_BP,replace=True)
time.sleep(6)
ID_LPVeins_ring_2 = removefilter(layerid=ID_LPVeins_ring_2,mask=ID_LA_Myo,replace=True)
time.sleep(6)
ID_LPVeins_ring_2 = removefilter(layerid=ID_LPVeins_ring_2,mask=ID_LPVeins_BP_2,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# Right pulmonary vein #1
ID_distMap = distancefilter(layerid=ID_RPVeins_BP_1)
time.sleep(6)
ID_RPVeins_ring_1 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_RPVeins_ring_1 = removefilter(layerid=ID_RPVeins_ring_1,mask=ID_LA_BP,replace=True)
time.sleep(6)
ID_RPVeins_ring_1 = removefilter(layerid=ID_RPVeins_ring_1,mask=ID_LA_Myo,replace=True)
time.sleep(6)
ID_RPVeins_ring_1 = removefilter(layerid=ID_RPVeins_ring_1,mask=ID_RPVeins_BP_1,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# Right pulmonary vein #2
ID_distMap = distancefilter(layerid=ID_RPVeins_BP_2)
time.sleep(6)
ID_RPVeins_ring_2 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_RPVeins_ring_2 = removefilter(layerid=ID_RPVeins_ring_2,mask=ID_LA_BP,replace=True)
time.sleep(6)
ID_RPVeins_ring_2 = removefilter(layerid=ID_RPVeins_ring_2,mask=ID_LA_Myo,replace=True)
time.sleep(6)
ID_RPVeins_ring_2 = removefilter(layerid=ID_RPVeins_ring_2,mask=ID_RPVeins_BP_2,replace=True)
time.sleep(6)
ID_RPVeins_ring_2 = removefilter(layerid=ID_RPVeins_ring_2,mask=ID_RPVeins_ring_1,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# LAA 
ID_distMap = distancefilter(layerid=ID_LAA_BP)
time.sleep(6)
ID_LAA_ring = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_LAA_ring = removefilter(layerid=ID_LAA_ring,mask=ID_LA_BP,replace=True)
time.sleep(6)
ID_LAA_ring = removefilter(layerid=ID_LAA_ring,mask=ID_LA_Myo,replace=True)
time.sleep(6)
ID_LAA_ring = removefilter(layerid=ID_LAA_ring,mask=ID_LAA_BP,replace=True)
time.sleep(6)
# ID_LAA_ring = removefilter(layerid=ID_LAA_ring,mask=ID_LPVeins_ring_1,replace=True)
# time.sleep(6)
ID_LPVeins_ring_1 = removefilter(layerid=ID_LPVeins_ring_1,mask=ID_LAA_ring,replace=True)
time.sleep(6)
ID_LAA_ring = removefilter(layerid=ID_LAA_ring,mask=ID_LPVeins_ring_2,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# Superior vena cava
ID_distMap = distancefilter(layerid=ID_SVC_BP)
time.sleep(6)
ID_SVC_ring = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_SVC_ring = removefilter(layerid=ID_SVC_ring,mask=ID_RA_BP,replace=True)
time.sleep(6)
ID_SVC_ring = removefilter(layerid=ID_SVC_ring,mask=ID_RA_Myo,replace=True)
time.sleep(6)
ID_SVC_ring = removefilter(layerid=ID_SVC_ring,mask=ID_SVC_BP,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

# Inferior vena cava
ID_distMap = distancefilter(layerid=ID_IVC_BP)
time.sleep(6)
ID_IVC_ring = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(6)
ID_IVC_ring = removefilter(layerid=ID_IVC_ring,mask=ID_RA_BP,replace=True)
time.sleep(6)
ID_IVC_ring = removefilter(layerid=ID_IVC_ring,mask=ID_RA_Myo,replace=True)
time.sleep(6)
ID_IVC_ring = removefilter(layerid=ID_IVC_ring,mask=ID_IVC_BP,replace=True)
time.sleep(6)
deletelayers(layers=[ID_distMap])

ID_distMap_LA_Myo = distancefilter(layerid=ID_LA_Myo)
ID_distMap_RA_Myo = distancefilter(layerid=ID_RA_Myo)
time.sleep(5)
ID_distMap_LA_Myo_th = threshold(layerid=ID_distMap_LA_Myo,lower_threshold=0.00,upper_threshold=ring_thickness)
ID_distMap_RA_Myo_th = threshold(layerid=ID_distMap_RA_Myo,lower_threshold=0.00,upper_threshold=ring_thickness)
time.sleep(5)
deletelayers(layers=[ID_distMap_LA_Myo,ID_distMap_RA_Myo])

ID_LPVeins_ring_1 = andfilter(layerid=ID_LPVeins_ring_1,mask=ID_distMap_LA_Myo_th,replace=True)
time.sleep(5)
ID_LPVeins_ring_2 = andfilter(layerid=ID_LPVeins_ring_2,mask=ID_distMap_LA_Myo_th,replace=True)
time.sleep(5)

ID_RPVeins_ring_1 = andfilter(layerid=ID_RPVeins_ring_1,mask=ID_distMap_LA_Myo_th,replace=True)
time.sleep(5)
ID_RPVeins_ring_2 = andfilter(layerid=ID_RPVeins_ring_2,mask=ID_distMap_LA_Myo_th,replace=True)
time.sleep(5)

ID_LAA_ring = andfilter(layerid=ID_LAA_ring,mask=ID_distMap_LA_Myo_th,replace=True)
time.sleep(5)

ID_SVC_ring = andfilter(layerid=ID_SVC_ring,mask=ID_distMap_RA_Myo_th,replace=True)
time.sleep(5)
ID_IVC_ring = andfilter(layerid=ID_IVC_ring,mask=ID_distMap_RA_Myo_th,replace=True)
time.sleep(6)

deletelayers(layers=[ID_distMap_LA_Myo_th,ID_distMap_RA_Myo_th])

# ---------------------------------------------------------------------------------------------------

# plane 1 (RPVeins_1)
ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_plane_1 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_1 = andfilter(layerid=ID_plane_1,mask=ID_RPVeins_BP_1,replace='true')
time.sleep(6)

ID_RPVeins_BP_1 = removefilter(layerid=ID_RPVeins_BP_1,mask=ID_plane_1,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 2 (RPVeins_2)
ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_plane_2 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_2 = andfilter(layerid=ID_plane_2,mask=ID_RPVeins_BP_2,replace='true')
time.sleep(6)

ID_RPVeins_BP_2 = removefilter(layerid=ID_RPVeins_BP_2,mask=ID_plane_2,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 3 (LPVeins_1)
ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_plane_3 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_3 = andfilter(layerid=ID_plane_3,mask=ID_LPVeins_BP_1,replace='true')
time.sleep(6)

ID_LPVeins_BP_1 = removefilter(layerid=ID_LPVeins_BP_1,mask=ID_plane_3,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 4 (LPVeins_2)
ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_plane_4 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_4 = andfilter(layerid=ID_plane_4,mask=ID_LPVeins_BP_2,replace='true')
time.sleep(6)

ID_LPVeins_BP_2 = removefilter(layerid=ID_LPVeins_BP_2,mask=ID_plane_4,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 5 (LAA)
ID_distMap = distancefilter(layerid=ID_LA_BP)
time.sleep(5)

ID_plane_5 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_5 = andfilter(layerid=ID_plane_5,mask=ID_LAA_BP,replace='true')
time.sleep(6)

ID_LAA_BP = removefilter(layerid=ID_LAA_BP,mask=ID_plane_5,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 6 (SVC)
ID_distMap = distancefilter(layerid=ID_RA_BP)
time.sleep(5)

ID_plane_6 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_6 = andfilter(layerid=ID_plane_6,mask=ID_SVC_BP,replace='true')
time.sleep(6)

ID_SVC_BP = removefilter(layerid=ID_SVC_BP,mask=ID_plane_6,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])

# plane 7 (IVC)
ID_distMap = distancefilter(layerid=ID_RA_BP)
time.sleep(5)

ID_plane_7 = threshold(layerid=ID_distMap,lower_threshold=0.00,upper_threshold=valve_WT)
time.sleep(6)
ID_plane_7 = andfilter(layerid=ID_plane_7,mask=ID_IVC_BP,replace='true')
time.sleep(6)

ID_IVC_BP = removefilter(layerid=ID_IVC_BP,mask=ID_plane_7,replace='true')
time.sleep(6)
deletelayers(layers=[ID_distMap])


# ---------------------------------------------------------------------------------------------------
set(stateid = ID_LV_BP + '::name',value='LV_BP_Final')
set(stateid = ID_RV_BP + '::name',value='RV_BP_Final')
set(stateid = ID_LV_Myo + '::name',value='LV_Myo_Final')
set(stateid = ID_RV_Myo + '::name',value='RV_Myo_Final')
set(stateid = ID_LA_Myo + '::name',value='LA_Myo_Final')
set(stateid = ID_RA_Myo + '::name',value='RA_Myo_Final')
set(stateid = ID_PArt_WT_new + '::name',value='PArt_WT')
set(stateid = ID_MV_temp + '::name',value='MV')
set(stateid = ID_TV_temp + '::name',value='TV')
set(stateid = ID_AV_temp + '::name',value='AV')
set(stateid = ID_PV_temp + '::name',value='PV')
set(stateid = ID_LPVeins_ring_1 + '::name',value='LPVeins_ring_1')
set(stateid = ID_LPVeins_ring_2 + '::name',value='LPVeins_ring_2')
set(stateid = ID_RPVeins_ring_1 + '::name',value='RPVeins_ring_1')
set(stateid = ID_RPVeins_ring_2 + '::name',value='RPVeins_ring_2')
set(stateid = ID_LAA_ring + '::name',value='LAA_ring')
set(stateid = ID_SVC_ring + '::name',value='SVC_ring')
set(stateid = ID_IVC_ring + '::name',value='IVC_ring')
set(stateid = ID_plane_1 + '::name',value='Plane_1')
set(stateid = ID_plane_2 + '::name',value='Plane_2')
set(stateid = ID_plane_3 + '::name',value='Plane_3')
set(stateid = ID_plane_4 + '::name',value='Plane_4')
set(stateid = ID_plane_5 + '::name',value='Plane_5')
set(stateid = ID_plane_6 + '::name',value='Plane_6')
set(stateid = ID_plane_7 + '::name',value='Plane_7')

filenameOut = '2016111001EP_ct_ed_label_maps_SVC_IVC_split_veins_myo_rings'
exportsegmentation(layers=[ID_LV_Myo,ID_RV_Myo,ID_LA_Myo,ID_RA_Myo,ID_Ao_WT,ID_PArt_WT_new,ID_MV_temp,ID_TV_temp,ID_AV_temp,ID_PV_temp,ID_LPVeins_ring_1,ID_LPVeins_ring_2,ID_RPVeins_ring_1,ID_RPVeins_ring_2,ID_LAA_ring,ID_SVC_ring,ID_IVC_ring,ID_plane_1,ID_plane_2,ID_plane_3,ID_plane_4,ID_plane_5,ID_plane_6,ID_plane_7],
                    file_path=filepath+'/'+filenameOut,mode='label_mask',extension='.nrrd',exporter='[NRRD Exporter]')
time.sleep(10)

deletelayers(layers=[ID_LA_BP,ID_RA_BP,ID_Ao_BP,ID_Ao_WT,ID_PArt_BP,ID_PArt_WT,ID_LPVeins_BP_1,ID_LPVeins_BP_2,ID_LAA_BP,ID_RPVeins_BP_1,ID_RPVeins_BP_2,ID_SVC_BP,ID_IVC_BP,ID_LV_Myo_extra])

# exec(open('/data/Dropbox/Segmentations/2016111001EP/py/generateValvePlane_Rosie.py').read())