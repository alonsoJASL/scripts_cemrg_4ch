# ttest_execute.py

from stats_utils import anova_test
from file_utils import load_json
from scipy import stats

EF_af_to_ra = [2.3, 2.143, 4.225, 2.876]
SV_af_to_ra = [2.798, 2.794, 8.901, 5.007]

EF_ra_to_rh = [0.862, 0.021, 0.68, 1.461]
SV_ra_to_rh = [1.701, 0.046, 1.941, 3.804]

t_EF_af_to_ra = stats.ttest_1samp(EF_af_to_ra, 0, alternative='greater')
t_SV_af_to_ra = stats.ttest_1samp(SV_af_to_ra, 0, alternative='greater')
t_EF_ra_to_rh = stats.ttest_1samp(EF_ra_to_rh, 0, alternative='greater')
t_SV_ra_to_rh = stats.ttest_1samp(SV_ra_to_rh, 0, alternative='greater')

print(t_EF_af_to_ra)
print(t_SV_af_to_ra)
print(t_EF_ra_to_rh)
print(t_SV_ra_to_rh)