import csv
import numpy as np 

def last_full_beat(data,BCL,AV_delay):
	# BCL and AV delay in ms
	lower = 2*int(BCL)-int(AV_delay)+40
	cropped_data = data[lower:-1]

	return cropped_data

def crop_data(data,start,end):
	cropped_data = data[start:end]

	return cropped_data

def prepare_pres_data(cycleFolder):
	LV = cycleFolder+"/cav.LV.csv"
	RV = cycleFolder+"/cav.RV.csv"
	LA = cycleFolder+"/cav.LA.csv"
	RA = cycleFolder+"/cav.RA.csv"
	
	LV_pres = []
	RV_pres = []
	LA_pres = []
	RA_pres = []
	
	with open(LV, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			LV_pres.append(row[1])
	csv_file.close
	LV_pres = LV_pres[2:len(LV_pres)]
	LV_pres = np.loadtxt(LV_pres, delimiter=",")

	with open(RV, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RV_pres.append(row[1])
	csv_file.close
	RV_pres = RV_pres[2:len(RV_pres)]
	RV_pres = np.loadtxt(RV_pres, delimiter=",")

	with open(LA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			LA_pres.append(row[1])
	csv_file.close
	LA_pres = LA_pres[2:len(LA_pres)]
	LA_pres = np.loadtxt(LA_pres, delimiter=",")

	with open(RA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RA_pres.append(row[1])
	csv_file.close
	RA_pres = RA_pres[2:len(RA_pres)]
	RA_pres = np.loadtxt(RA_pres, delimiter=",")

	return LV_pres,RV_pres,LA_pres,RA_pres

def prepare_vol_data(cycleFolder):
	LV = cycleFolder+"/cav.LV.csv"
	RV = cycleFolder+"/cav.RV.csv"
	LA = cycleFolder+"/cav.LA.csv"
	RA = cycleFolder+"/cav.RA.csv"
	
	LV_vol = []
	RV_vol = []
	LA_vol = []
	RA_vol = []

	with open(LV, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			LV_vol.append(row[2])
	csv_file.close
	LV_vol = LV_vol[2:len(LV_vol)]
	LV_vol = np.loadtxt(LV_vol, delimiter=",")

	with open(RV, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RV_vol.append(row[2])
	csv_file.close
	RV_vol = RV_vol[2:len(RV_vol)]
	RV_vol = np.loadtxt(RV_vol, delimiter=",")

	with open(LA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			LA_vol.append(row[2])
	csv_file.close
	LA_vol = LA_vol[2:len(LA_vol)]
	LA_vol = np.loadtxt(LA_vol, delimiter=",")

	with open(RA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RA_vol.append(row[2])
	csv_file.close
	RA_vol = RA_vol[2:len(RA_vol)]
	RA_vol = np.loadtxt(RA_vol, delimiter=",")

	return LV_vol,RV_vol,LA_vol,RA_vol

def prepare_Ao_data(cycleFolder):
	Ao_data = cycleFolder+"/tube.AO.csv"
	
	Ao_pres = []
	
	with open(Ao_data, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			Ao_pres.append(row[1])
	csv_file.close
	Ao_pres = Ao_pres[2:len(Ao_pres)]
	Ao_pres = np.loadtxt(Ao_pres, delimiter=",")

	return Ao_pres

def split_ejection(LV_pres,Ao_pres):
	# inputs = lv pressure and aortic pressure
	# output = index of the start and end points of each ejection phase	

	Ao_eject_pres=[]
	eject_starts=[]
	eject_ends=[]

	for i,p in enumerate(Ao_pres):
		if LV_pres[i] - Ao_pres[i] >= 0.5:	# condition for ejection
			Ao_eject_pres.append(Ao_pres[i])	# saves the value of aortic pressure if in ejection phase
		else:			
			Ao_eject_pres.append(0)

	for i,p in enumerate(Ao_eject_pres):
		if i < len(Ao_eject_pres)-1:	# keeps i+1 in range
			if Ao_eject_pres[i] == 0:
				if Ao_eject_pres[i+1] > 0:
					eject_starts.append(i+1)	# saves index if ejection begins

			if Ao_eject_pres[i] > 0:
				if Ao_eject_pres[i+1] == 0:
					eject_ends.append(i+1)		# saves index if ejection ends

	# Must remove any artifical start/end ejections caused by oscillations
	to_be_removed=[] 

	for i in range(len(eject_starts)-1):
		if abs(eject_starts[i] - eject_starts[i+1]) < 50:	# check for ejection_starts within short timeframe
			to_be_removed.append(i)
			to_be_removed.append(i+1)

	eject_starts = np.unique(eject_starts)		
	eject_starts = np.delete(eject_starts,to_be_removed)

	to_be_removed=[]

	for i in range(len(eject_ends)-1):
		if abs(eject_ends[i] - eject_ends[i+1]) < 50:	# checks for ejection_ends within short timeframe
			to_be_removed.append(i)
			to_be_removed.append(i+1)

	eject_ends = np.unique(eject_ends) # some indices will be duplicated causing np.delete to crash if not resolved	
	eject_ends = np.delete(eject_ends,to_be_removed)

	# If sim ends mid cycle, set the last time point as an ejection_ends index
	if len(eject_starts) - len(eject_ends) == 1:
		eject_ends = np.append(eject_ends,len(Ao_eject_pres)-1)


	return eject_starts, eject_ends

def find_ejection(LV_vol):

	vol_ejecting=[]
	eject_starts=[]
	eject_ends=[]

	for i,v in enumerate(LV_vol):
		if i < len(LV_vol)-5:

			if LV_vol[i]-LV_vol[i+5] <= 0.05:
				vol_ejecting.append(0)
			else:
				vol_ejecting.append(LV_vol[i])

	for i,v in enumerate(vol_ejecting):
		if i < len(vol_ejecting)-1:	# keeps i+1 in range

			if vol_ejecting[i] == 0:
				if vol_ejecting[i+1] > 0:
					eject_starts.append(i+1)		# saves index if ejection starts

			if vol_ejecting[i] > 0:
				if vol_ejecting[i+1] == 0:
					eject_ends.append(i)		# saves index if ejection ends

	# Must remove any artifical start/end ejections caused by oscillations
	to_be_removed=[]

	for i in range(len(eject_ends)-1):
		if abs(eject_ends[i] - eject_starts[i+1]) < 100:	# checks for ejection_ends within short timeframe
			to_be_removed.append(i)

	eject_ends = np.delete(eject_ends,to_be_removed)

	to_be_removed_starts = [x+1 for x in to_be_removed]
	eject_starts = np.delete(eject_starts,to_be_removed_starts)

	# If sim ends mid cycle, set the last time point as an ejection_ends index
	if len(eject_starts) - len(eject_ends) == 1:
		eject_ends = np.append(eject_ends,len(LV_vol)-1)

	return eject_starts, eject_ends

def find_mapde(eject_starts,eject_ends,Ao_pres):
	# Mean Aortic Pressure During Ejection

	MAPDE=[]
	for i in range(len(eject_starts)):
		APDE = Ao_pres[eject_starts[i]:eject_ends[i]]
		MAPDE.append(np.mean(APDE))

	return MAPDE

def find_sv(LV_vol):
	eject_starts, eject_ends = find_ejection(LV_vol)

	SV = []
	for i,t in enumerate(eject_starts):
		vol_ejecting = LV_vol[eject_starts[i]:eject_ends[i]]
		SV.append(max(vol_ejecting) - min(vol_ejecting))

	return SV

def find_vol_max(LV_vol):
	eject_starts, eject_ends = find_ejection(LV_vol)

	vol_max = []
	for i,t in enumerate(eject_starts):
		vol_ejecting = LV_vol[eject_starts[i]:eject_ends[i]]
		vol_max.append(max(vol_ejecting))

	return vol_max

def find_vol_min(LV_vol):
	eject_starts, eject_ends = find_ejection(LV_vol)

	vol_min = []
	for i,t in enumerate(eject_starts):
		vol_ejecting = LV_vol[eject_starts[i]:eject_ends[i]]
		vol_min.append(min(vol_ejecting))

	return vol_min

def find_stroke_work(MAPDE,SV):
	SW = np.zeros(len(MAPDE))
	for i in range(len(MAPDE)):
		SW[i] = MAPDE[i]*SV[i]



	return SW

def ml_to_m3(vol_ml):
	vol_m3 = [i * 1e-6 for i in vol_ml]

	return vol_m3

def mmHg_to_Pa(pres_mmHg):
	pres_Pa = [i * 133.322 for i in pres_mmHg]

	return pres_Pa

def ms_to_s(time_ms):
	time_s = [i * 1e-3 for i in time_ms]

	return time_s
