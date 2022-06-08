import time
#import numpy as np
import json
import string

def push_inside(ID_pusher_wall,ID_pusher_BP,ID_pushed_wall,ID_pushed_BP,pushed_WT):

    ID_pusher = orfilter(layerid=ID_pusher_BP,mask=ID_pusher_wall,replace='false') # Whole pusher
    time.sleep(10)
    ID_pusher_DistMap = distancefilter(layerid=ID_pusher)
    time.sleep(10)
    ID_new_pushed_wall = threshold(layerid=ID_pusher_DistMap,lower_threshold=pushed_WT,upper_threshold=-0.01)
    time.sleep(10)
    ID_new_pushed_wall = andfilter(layerid=ID_new_pushed_wall,mask=ID_pushed_BP,replace='true')
    time.sleep(10)

    ID_pushed_wall = removefilter(layerid=ID_pushed_wall,mask=ID_pusher,replace=True)
    time.sleep(10)
    ID_pushed_wall = orfilter(layerid=ID_pushed_wall,mask=ID_new_pushed_wall,replace='true')
    time.sleep(10)

    ID_pushed_BP = removefilter(layerid = ID_pushed_BP, mask = ID_pushed_wall, replace = True)
    time.sleep(10)

    deletelayers(layers = [ID_pusher_DistMap,ID_new_pushed_wall,ID_pusher])

    return([ID_pushed_BP,ID_pushed_wall])

filenames = "/seg_s2b.nrrd" 
filepath = "/data/Dropbox/henry/segmentations/"
InitialSegmentation = importlayer(filename=filepath + '/' + filenames,importer='[Teem Importer]',mode='data',inputfiles_id=5)

#ID_Back   = threshold(layerid=InitialSegmentation[0],lower_threshold=0.00,upper_threshold=0.00) # background          
ID_LV_BP = threshold(layerid=InitialSegmentation[0],lower_threshold=1.00,upper_threshold=1.00) # LV Blood pool
ID_LV_Myo = threshold(layerid=InitialSegmentation[0],lower_threshold=2.00,upper_threshold=2.00) # LV myocardium       
ID_RV_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=3.00,upper_threshold=3.00) # RV blood pool    
ID_LA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=4.00,upper_threshold=4.00) # LA blood pool       
ID_RA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=5.00,upper_threshold=5.00) # RA blood pool	
ID_Ao_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=6.00,upper_threshold=6.00) # Aorta blood pool    
ID_PArt_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=7.00,upper_threshold=7.00) # Pulm artery blood pool    
ID_LPVeins_BP_1  = threshold(layerid=InitialSegmentation[0],lower_threshold=8.00,upper_threshold=8.00) # Left pulmonary 1 vein blood pool    
ID_LPVeins_BP_2  = threshold(layerid=InitialSegmentation[0],lower_threshold=9.00,upper_threshold=9.00) # Left pulmonary 2 vein blood pool  
ID_RPVeins_BP_1  = threshold(layerid=InitialSegmentation[0],lower_threshold=10.00,upper_threshold=10.00) # Right pulmonary 1 vein blood pool    
ID_RPVeins_BP_2  = threshold(layerid=InitialSegmentation[0],lower_threshold=11.00,upper_threshold=11.00) # Right pulmonary 2 vein blood pool    
ID_LAA_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=12.00,upper_threshold=12.00) # Left atrial appendage blood pool
ID_SVC_BP = threshold(layerid=InitialSegmentation[0],lower_threshold=13.00,upper_threshold=13.00) # SVC blood pool    
ID_IVC_BP  = threshold(layerid=InitialSegmentation[0],lower_threshold=14.00,upper_threshold=14.00) # IVC blood pool
time.sleep(4)
deletelayers(layers = InitialSegmentation)

LV_WT = 2.00;
RV_WT = 3.50;
LA_WT = 2.00;
RA_WT = 2.00;
Ao_WT = 2.00;
PArt_WT = 2.00;

# ---------------------------- #
# create LV outflow tract myo

ID_LV_DistMap = distancefilter(layerid=ID_LV_BP)
time.sleep(10)

ID_LV_neck = threshold(layerid=ID_LV_DistMap,lower_threshold=-0.01,upper_threshold=LV_WT)
time.sleep(5)

ID_LV_neck = removefilter(layerid=ID_LV_neck,mask=ID_Ao_BP,replace=True)
time.sleep(5)

ID_LV_neck = removefilter(layerid=ID_LV_neck,mask=ID_LV_BP,replace=True)
time.sleep(5)

ID_LV_neck = removefilter(layerid=ID_LV_neck,mask=ID_LA_BP,replace=True)
time.sleep(5)

ID_LV_neck = removefilter(layerid=ID_LV_neck,mask=ID_LV_Myo,replace=True)
time.sleep(5)

ID_LV_Myo_new = orfilter(layerid=ID_LV_neck,mask=ID_LV_Myo,replace='false')
time.sleep(5)

set(stateid = ID_LV_neck + '::name',value='LV_neck')
set(stateid = ID_LV_Myo_new + '::name',value='LV_Myo_neck')

deletelayers(layers=ID_LV_DistMap)

# ---------------------------- #

ID_RV_BP = removefilter(layerid=ID_RV_BP,mask=ID_LV_Myo_new,replace=True)
time.sleep(10)

# --------------------------------------------------------------------------------------------------
# Aorta Dilation - Wall thickness
# --------------------------------------------------------------------------------------------------

ID_Ao_DistMap = distancefilter(layerid=ID_Ao_BP)
time.sleep(10)

ID_Ao_WT = threshold(layerid=ID_Ao_DistMap,lower_threshold=-0.01,upper_threshold=Ao_WT)
time.sleep(5)

ID_Ao_WT = removefilter(layerid=ID_Ao_WT,mask=ID_Ao_BP,replace=True)
time.sleep(5)

ID_Ao_WT = removefilter(layerid=ID_Ao_WT,mask=ID_LV_BP,replace=True)
time.sleep(5)

ID_LV_Myo_new = removefilter(layerid=ID_LV_Myo_new,mask=ID_Ao_WT,replace=True)
time.sleep(5)

deletelayers(layers=ID_Ao_DistMap)

filenames = "aorta_slicer.nrrd"

SlicerSegmentation = importlayer(filename=filepath + '/' + filenames,importer='[Teem Importer]',mode='data',inputfiles_id=5) 

ID_aorta_slicer   = threshold(layerid=SlicerSegmentation[0],lower_threshold=1.00,upper_threshold=1.00) # aorta slicer
time.sleep(4)
deletelayers(layers = SlicerSegmentation)

ID_Ao_WT = removefilter(layerid=ID_Ao_WT,mask=ID_aorta_slicer,replace=True)
time.sleep(4)

ID_LV_Ao_WT = orfilter(layerid=ID_LV_Myo_new,mask=ID_Ao_WT,replace='false')
ID_LV_Ao_BP = orfilter(layerid=ID_LV_BP,mask=ID_Ao_BP,replace='false')

set(stateid = ID_Ao_WT + '::name',value='Aorta_Wall')
set(stateid = ID_LV_Ao_WT + '::name',value='LV_myo_Ao_wall')
set(stateid = ID_LV_Ao_BP + '::name',value='LV_BP_Ao_BP')

# --------------------------------------------------------------------------------------------------
# Pulmonary artery Dilation - Wall thickness
# --------------------------------------------------------------------------------------------------

ID_PArt_DistMap = distancefilter(layerid=ID_PArt_BP)
time.sleep(10)

ID_PArt_WT = threshold(layerid=ID_PArt_DistMap,lower_threshold=-0.01,upper_threshold=PArt_WT)
time.sleep(5)

deletelayers(layers=ID_PArt_DistMap)

ID_PArt_WT = removefilter(layerid=ID_PArt_WT,mask=ID_PArt_BP,replace=True)
time.sleep(5)

ID_PArt_WT = removefilter(layerid=ID_PArt_WT,mask=ID_RV_BP,replace=True)
time.sleep(5)

filenames = "PArt_slicer.nrrd"

SlicerSegmentation = importlayer(filename=filepath + '/' + filenames,importer='[Teem Importer]',mode='data',inputfiles_id=5) 

ID_PArt_slicer   = threshold(layerid=SlicerSegmentation[0],lower_threshold=1.00,upper_threshold=1.00) # aorta slicer
time.sleep(4)
deletelayers(layers = SlicerSegmentation)

ID_PArt_WT = removefilter(layerid=ID_PArt_WT,mask=ID_PArt_slicer,replace=True)
time.sleep(4)

set(stateid = ID_PArt_WT + '::name',value='PArt_Wall')


##### TO FINI

# ID_LV_Myo_new = removefilter(layerid=ID_LV_Myo_new,mask=ID_PArt_WT,replace=True)
# time.sleep(5)

# deletelayers(layers=ID_Ao_DistMap)

# ID_LV_Ao_WT = orfilter(layerid=ID_LV_Myo_new,mask=ID_Ao_WT,replace='false')
# ID_LV_Ao_BP = orfilter(layerid=ID_LV_BP,mask=ID_Ao_BP,replace='false')

# set(stateid = ID_Ao_WT + '::name',value='Aorta_Wall')
# set(stateid = ID_LV_Ao_WT + '::name',value='LV_myo_Ao_wall')
# set(stateid = ID_LV_Ao_BP + '::name',value='LV_BP_Ao_BP')

# --------------------------------------------------------------------------------------------------
# RV Dilation - Myocardium
# --------------------------------------------------------------------------------------------------

ID_RV_DistMap = distancefilter(layerid=ID_RV_BP)
time.sleep(10)

ID_RV_Myo = threshold(layerid=ID_RV_DistMap,lower_threshold=RV_WT,upper_threshold=-0.01)
time.sleep(5)

deletelayers(layers=ID_RV_DistMap)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_RV_BP,replace=True)     # remove RA BP
time.sleep(5)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_RA_BP,replace=True)     # remove RA BP
time.sleep(5)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_LV_Myo,replace=True)     # remove RA BP
time.sleep(5)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_PArt_BP,replace=True)     # remove RA BP
time.sleep(5)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_PArt_WT,replace=True)     # remove RA BP
time.sleep(5)

set(stateid = ID_RV_BP + '::name',value='RV_BP')
set(stateid = ID_RV_Myo + '::name',value='RV_myo')

# --------------------------------------------------------------------------------------------------
# LA Dilation - Myocardium
# --------------------------------------------------------------------------------------------------

ID_LA_DistMap = distancefilter(layerid=ID_LA_BP)
time.sleep(10)

ID_LA_Myo = threshold(layerid=ID_LA_DistMap,lower_threshold=LA_WT,upper_threshold=-0.01)
time.sleep(5)

deletelayers(layers=ID_LA_DistMap)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LA_BP,replace=True)     
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LV_BP,replace=True)     # remove LV
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_RV_BP,replace=True)  # remove RV blood pool
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_RV_Myo,replace=True)
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LAA_BP,replace=True)
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_RPVeins_BP_1,replace=True)
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_RPVeins_BP_2,replace=True)
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LPVeins_BP_1,replace=True)
time.sleep(5)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LPVeins_BP_2,replace=True)
time.sleep(5)

set(stateid = ID_LA_BP + '::name',value='LA_BP')
set(stateid = ID_LA_Myo + '::name',value='LA_Myo')

# --------------------------------------------------------------------------------------------------
# RA Dilation - Myocardium
# --------------------------------------------------------------------------------------------------

ID_RA_DistMap = distancefilter(layerid=ID_RA_BP)
time.sleep(10)

ID_RA_Myo = threshold(layerid=ID_RA_DistMap,lower_threshold=-0.01,upper_threshold=RA_WT)
time.sleep(5)

deletelayers(layers=ID_RA_DistMap)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_RA_BP,replace=True)     
time.sleep(5)
ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_RV_BP,replace=True)  # remove RV blood pool
time.sleep(5)
ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_RV_Myo,replace=True)  # remove RV myocardium
time.sleep(5)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_SVC_BP,replace=True)
time.sleep(5)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_IVC_BP,replace=True)
time.sleep(5)

set(stateid = ID_RA_BP + '::name',value='RA_BP')
set(stateid = ID_RA_Myo + '::name',value='RA_Myo')

# --------------------------------------------------------------------------------------------------
# RA is pushed by the LA
# --------------------------------------------------------------------------------------------------

new_RA = push_inside(ID_LA_Myo,ID_LA_BP,ID_RA_Myo,ID_RA_BP,RA_WT)
ID_RA_BP = new_RA[0]
ID_RA_Myo = new_RA[1]
time.sleep(10)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_LA_Myo,replace=True)  # remove RV blood pool
time.sleep(5)

ID_RA_BP = removefilter(layerid=ID_RA_BP,mask=ID_LA_Myo,replace=True)  # remove RV blood pool
time.sleep(5)

# --------------------------------------------------------------------------------------------------
# RA is pushed by the aorta and the LV
# --------------------------------------------------------------------------------------------------

new_RA = push_inside(ID_LV_Ao_WT,ID_LV_Ao_BP,ID_RA_Myo,ID_RA_BP,RA_WT)
ID_RA_BP = new_RA[0]
ID_RA_Myo = new_RA[1]
time.sleep(10)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

ID_RA_BP = removefilter(layerid=ID_RA_BP,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

# --------------------------------------------------------------------------------------------------
# LA is pushed by the aorta
# --------------------------------------------------------------------------------------------------

new_LA = push_inside(ID_Ao_WT,ID_Ao_BP,ID_LA_Myo,ID_LA_BP,LA_WT)
ID_LA_BP = new_LA[0]
ID_LA_Myo = new_LA[1]

# --------------------------------------------------------------------------------------------------
# PArt is pushed by the aorta and the LV
# --------------------------------------------------------------------------------------------------

new_PArt = push_inside(ID_LV_Ao_WT,ID_LV_Ao_BP,ID_PArt_WT,ID_PArt_BP,PArt_WT)
ID_PArt_BP = new_PArt[0]
ID_PArt_WT = new_PArt[1]
time.sleep(10)

ID_PArt_WT = removefilter(layerid=ID_PArt_WT,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

ID_PArt_BP = removefilter(layerid=ID_PArt_BP,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

# --------------------------------------------------------------------------------------------------
# RV is pushed by the aorta and the LV
# --------------------------------------------------------------------------------------------------

ID_RV_BP_temp = duplicatelayer(layerid=ID_RV_BP)

RV_WT_neck = 2.00
new_RV = push_inside(ID_LV_Ao_WT,ID_LV_Ao_BP,ID_RV_Myo,ID_RV_BP,RV_WT_neck)
ID_RV_BP = new_RV[0]
ID_RV_Myo = new_RV[1]
time.sleep(10)

ID_LV_Myo_DistMap = distancefilter(layerid=ID_LV_Myo)
time.sleep(10)

ID_septum = threshold(layerid=ID_LV_Myo_DistMap,lower_threshold=0.0,upper_threshold=RV_WT_neck)
time.sleep(10)

deletelayers(layers=ID_LV_Myo_DistMap)

ID_septum = andfilter(layerid=ID_septum,mask=ID_RV_BP_temp,replace='true')
time.sleep(10)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_septum,replace='true')
time.sleep(10)

ID_RV_BP = orfilter(layerid=ID_RV_BP,mask=ID_septum,replace='true')
time.sleep(10)

# ----------------------------------------------------------------------------------------------------
# final corrections
# ----------------------------------------------------------------------------------------------------

ID_LV_neck_DistMap = distancefilter(layerid=ID_LV_neck)
time.sleep(10)

ID_RV_neck = threshold(layerid=ID_LV_neck_DistMap,lower_threshold=0.0,upper_threshold=RV_WT_neck)
time.sleep(10)

deletelayers(layers=ID_LV_neck_DistMap)

ID_RV_neck = andfilter(layerid=ID_RV_neck,mask=ID_RV_BP,replace=True)
time.sleep(10)

ID_RV_Myo = orfilter(layerid=ID_RV_Myo,mask=ID_RV_neck,replace=True)
time.sleep(10)

ID_RV_BP = removefilter(layerid=ID_RV_BP,mask=ID_RV_neck,replace=True)
time.sleep(10)

ID_LA_Myo = removefilter(layerid=ID_LA_Myo,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

ID_RV_Myo = removefilter(layerid=ID_RV_Myo,mask=ID_LV_Ao_WT,replace=True)
time.sleep(10)

ID_RV_Myo = dilatefilter(layerid=ID_RV_Myo,mask=ID_RA_Myo,radius=5,invert_mask=False,replace=True)
time.sleep(10)

ID_RA_Myo = removefilter(layerid=ID_RA_Myo,mask=ID_RV_Myo,replace=True)
time.sleep(10)

# ---------------------------------------------------------------------------------------------------
filenameOut = 'seg_s3'
exportsegmentation(layers=[ID_LV_BP,ID_LV_Myo_new,ID_RV_BP,ID_RV_Myo,ID_LA_BP,ID_LA_Myo,ID_RA_BP,ID_RA_Myo,ID_Ao_BP,ID_Ao_WT,ID_PArt_BP,ID_PArt_WT,ID_LPVeins_BP_1,ID_LPVeins_BP_2,ID_LAA_BP,ID_RPVeins_BP_1,ID_RPVeins_BP_2,ID_SVC_BP,ID_IVC_BP],
                   file_path=filepath+'/'+filenameOut,mode='label_mask',extension='.nrrd',exporter='[NRRD Exporter]')
time.sleep(10)

deletelayers(layers=[ID_PArt_BP,ID_Ao_BP,ID_LV_Myo,ID_LV_BP,ID_LV_Ao_WT,ID_LV_Ao_BP,ID_RV_BP_temp,ID_septum,ID_RV_neck,ID_PArt_slicer,ID_aorta_slicer,ID_SVC_BP,ID_IVC_BP,ID_LAA_BP,ID_LPVeins_BP_1,ID_LPVeins_BP_2,ID_RPVeins_BP_1,ID_RPVeins_BP_2])



# exec(open("/data/Dropbox/henry/segmentations/seg_scripts/create_myo.py").read())
