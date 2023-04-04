import numpy as numpy
import json
import argparse
import os

parser = argparse.ArgumentParser(description='To run: python3 generate_act_times.py [cl_1] [cl_2] [cl_3]')
parser.add_argument("bcl_1")
parser.add_argument("bcl_2")
parser.add_argument("bcl_3")
args = parser.parse_args()
CL1 = args.bcl_1
CL2 = args.bcl_2
CL3 = args.bcl_3

# activation times default set-up
CL = [float(CL1),float(CL2),float(CL3)]
CL = CL + CL + CL
ERP = [i*0.9 for i in CL]
AV_d = [i*0.1 for i in CL]
AA_d = [i*0.05 for i in CL]
VV_d = [i*0 for i in CL]
SA_RA_d = [i*0 for i in CL]
RA_AV_d = [i*0 for i in CL]
RA_RV_d = [i*0.1 for i in CL]
LA_LV_d = [i*0.1 for i in CL]

CL_str_lst = [str(int(cl)) for cl in CL]
CL_str = ' '.join(CL_str_lst)

ERP_str_lst = [str(int(erp)) for erp in ERP]
ERP_str = ' '.join(ERP_str_lst)

AV_d_str_lst = [str(int(i)) for i in AV_d]
AV_d_str = ' '.join(AV_d_str_lst)

AA_d_str_lst = [str(int(i)) for i in AA_d]
AA_d_str = ' '.join(AA_d_str_lst)

VV_d_str_lst = [str(int(i)) for i in VV_d]
VV_d_str = ' '.join(VV_d_str_lst)

SA_RA_d_str_lst = [str(int(i)) for i in SA_RA_d]
SA_RA_d_str = ' '.join(SA_RA_d_str_lst)

RA_AV_d_str_lst = [str(int(i)) for i in RA_AV_d]
RA_AV_d_str = ' '.join(RA_AV_d_str_lst)

RA_RV_d_str_lst = [str(int(i)) for i in RA_RV_d]
RA_RV_d_str = ' '.join(RA_RV_d_str_lst)

LA_LV_d_str_lst = [str(int(i)) for i in LA_LV_d]
LA_LV_d_str = ' '.join(LA_LV_d_str_lst)

json_name = 'act_'+CL1+'_'+CL2+'_'+CL3+'.json'

f = open(json_name, "w")
f.write("{\n")
f.write('  "Cycle length [ms]": ')
f.write(CL_str+',\n')
f.write('  "Effective refractory period": ')
f.write(ERP_str+',\n')
f.write('  "AV delay [ms]": ')
f.write(AV_d_str+',\n')
f.write('  "AA delay [ms]": ')
f.write(AA_d_str+',\n')
f.write('  "VV delay [ms]": ')
f.write(VV_d_str+',\n')
f.write('  "SA RA delay [ms]": ')
f.write(SA_RA_d_str+',\n')
f.write('  "RA AV delay [ms]": ')
f.write(RA_AV_d_str+',\n')
f.write('  "RA RV delay [ms]": ')
f.write(RA_RV_d_str+',\n')
f.write('  "LA LV delay [ms]": ')
f.write(LA_LV_d_str+'\n')
f.write("}\n")
f.close()

# act_dictionary = {
#   "Cycle length [ms]": CL[0] CL[1] CL[2] CL[0] CL[1] CL[2] CL[0] CL[1] CL[2],
#   "Effective refractory period": ERP[0] ERP[1] ERP[2] ERP[0] ERP[1] ERP[2] ERP[0] ERP[1] ERP[2],
#   "AV delay [ms]": AV_d[0] AV_d[1] AV_d[2] AV_d[0] AV_d[1] AV_d[2] AV_d[0] AV_d[1] AV_d[2],
#   "AA delay [ms]": AA_d[0] AA_d[1] AA_d[2] AA_d[0] AA_d[1] AA_d[2] AA_d[0] AA_d[1] AA_d[2],
#   "VV delay [ms]": VV_d[0] VV_d[1] VV_d[2] VV_d[0] VV_d[1] VV_d[2] VV_d[0] VV_d[1] VV_d[2],
#   "SA RA delay [ms]": SA_RA_d[0] SA_RA_d[1] SA_RA_d[2] SA_RA_d[0] SA_RA_d[1] SA_RA_d[2] SA_RA_d[0] SA_RA_d[1] SA_RA_d[2],
#   "RA AV delay [ms]": RA_AV_d[0] RA_AV_d[1] RA_AV_d[2] RA_AV_d[0] RA_AV_d[1] RA_AV_d[2] RA_AV_d[0] RA_AV_d[1] RA_AV_d[2],
#   "RA RV delay [ms]": RA_RV_d[0] RA_RV_d[1] RA_RV_d[2] RA_RV_d[0] RA_RV_d[1] RA_RV_d[2] RA_RV_d[0] RA_RV_d[1] RA_RV_d[2],
#   "LA LV delay [ms]": LA_LV_d[0] LA_LV_d[1] LA_LV_d[2] LA_LV_d[0] LA_LV_d[1] LA_LV_d[2] LA_LV_d[0] LA_LV_d[1] LA_LV_d[2]
# }

# Convert dictionary to json using json.dumps
