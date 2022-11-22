import csv
import numpy as np 

def last_full_beat(data,BCL,AV_delay):
	# BCL and AV delay in ms
	lower = 2*int(BCL)-int(AV_delay)
	cropped_data = data[lower-3:-1]

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
			LV_vol.append(row[1])
	csv_file.close
	LV_vol = LV_vol[2:len(LV_vol)]
	LV_vol = np.loadtxt(LV_vol, delimiter=",")

	with open(RV, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RV_vol.append(row[1])
	csv_file.close
	RV_vol = RV_vol[2:len(RV_vol)]
	RV_vol = np.loadtxt(RV_vol, delimiter=",")

	with open(LA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			LA_vol.append(row[1])
	csv_file.close
	LA_vol = LA_vol[2:len(LA_vol)]
	LA_vol = np.loadtxt(LA_vol, delimiter=",")

	with open(RA, newline='') as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		for row in csv_reader:
			RA_vol.append(row[1])
	csv_file.close
	RA_vol = RA_vol[2:len(RA_vol)]
	RA_vol = np.loadtxt(RA_vol, delimiter=",")

	return LV_vol,RV_vol,LA_vol,RA_vol