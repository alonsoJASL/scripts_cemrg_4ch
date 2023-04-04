import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats
from bioinfokit.analys import stat
from file_utils import *

def anova_test(json_file,
			   simulations_list,
		   	   metric,
		   	   stats_output_file):

	data = load_json(json_file)

	extracted_data = {}

	print('Comparing metric '+metric+'...')
	for s in simulations_list:
		if s not in data:
			raise Exception('Simulation not found.')
		else:
			print('Using '+s+'...')
			extracted_data[s] = data[s][metric]

	df = pd.DataFrame.from_dict(extracted_data)
	df_melt = pd.melt(df.reset_index(), id_vars=['index'], value_vars=simulations_list)
	df_melt.columns = ['index', 'treatments', 'value']

	# fvalue, pvalue = stats.f_oneway(df['baseline'], df['CRT'], df['HBP_Selective'], df['LBP_Selective_optAVD'])

	# print(pvalue)

	res = stat()
	res.tukey_hsd(df=df_melt, res_var='value', xfac_var='treatments', anova_model='value ~ C(treatments)')
	pvalues = res.tukey_summary

	pvalues.to_csv(stats_output_file)
	

