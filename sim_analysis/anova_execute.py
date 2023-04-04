# anova_execute.py

from stats_utils import anova_test
from file_utils import load_json
from scipy import stats

# anova_test("SUMMARY_final.json",
# 		   ["AF","Rh_control","Ra_control"],
# 		    "EF",
# 		   	"./hrs_ptest.csv")

DATA = load_json("SUMMARY_final.json")
# DATA = load_json("SUMMARY_final_stroke_vol.json")

print(stats.ttest_rel(DATA["AF"]["EF"],DATA["Rh_control"]["EF"]))
print(stats.ttest_rel(DATA["AF"]["EF"],DATA["Ra_control"]["EF"]))
print(stats.ttest_rel(DATA["Ra_control"]["EF"],DATA["Rh_control"]["EF"]))


# print(stats.ttest_rel(DATA["AF"]["SV"],DATA["Rh_control"]["SV"]))
# print(stats.ttest_rel(DATA["AF"]["SV"],DATA["Ra_control"]["SV"]))
# print(stats.ttest_rel(DATA["Ra_control"]["SV"],DATA["Rh_control"]["SV"]))
