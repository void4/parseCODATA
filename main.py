from glob import glob
import re
from collections import defaultdict, Counter
from math import log
import matplotlib.pyplot as plt

paths = sorted(glob("CODATA/allascii_*.txt"))

years = [int(path.split(".")[0].split("_")[-1]) for path in paths]

print(years)

lastyear = max(years)
firstyear = min(years)
rng = lastyear - firstyear

data = defaultdict(list)

def splitUncertainty(value):

	value = value.replace(" ", "")

	purevalue = re.sub(r"\(.*?\)", "", value)
	rematch = re.search(r"\((.*?)\)", value)

	pureuncertainty = rematch.group(1) if rematch else None
	
	if pureuncertainty:
		pureuncertainty = "0." + "0" * (value.index("(") - value.index(".") - 1 - len(pureuncertainty)) + pureuncertainty
		
		if "e" in purevalue:
			pureuncertainty += purevalue[purevalue.index("e"):]

	return purevalue, pureuncertainty

for path in paths:
	year = int(path.split(".")[0].split("_")[-1])

	with open(path) as f:
		lines = f.read().splitlines()
	
	rows = []
	start = False
	for line in lines:
		if line.startswith("---"):
			start = True
			continue
		
		if not start:
			continue
		
		line = re.split(r"\s{2,}", line.strip())
		
		if len(line) == 2:
			name, value = line
			unit = None
			value, uncertainty = splitUncertainty(value)
		elif len(line) == 3:
			name, value, unit = line
			value, uncertainty = splitUncertainty(value)
		elif len(line) == 4:
			name, value, uncertainty, unit = line
		else:
			print(line)
		
		value = value.replace(" ", "")
		if uncertainty:
			uncertainty = uncertainty.replace(" ", "")
		
		data[name].append([str(year), value, uncertainty, unit])
	
	#print(rows)

testkey = "electron mass"
print(testkey)
for year in data[testkey]:
	print("\t\t".join(year))

def isfloat(v):
	try:
		float(v)
		return True
	except ValueError:
		pass
	return False

for name, years in data.items():
	if len(years) == 6 and all([year[2] is not None and isfloat(year[2]) and float(year[2]) != 0 for year in years]):
		
		if " in " in name or " relationship" in name or " equivalent" in name or "atomic unit" in name or "molar " in name:
			continue
		
		#for year in years:
		#	print("%.2f" % log(float(years[0][2])/float(year[2]), 10))
		
		xs = []
		ys = []
		for year in years:
			xs.append(int(year[0]))
			ys.append(log(float(years[0][2])/float(year[2]), 10))
		
		plt.plot(xs, ys, label=name)
		
		decimaldigits = log(float(years[0][2])/float(years[-1][2]), 10)
		if decimaldigits == 0:
			continue
		print(name)
		print("%.2f digits" % decimaldigits, "%.2f y/dgt" % (rng/decimaldigits))

plt.title(f"number of decimal digits improved compared to first year ({firstyear}-{lastyear})")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.tight_layout()
plt.savefig("plot.png")
plt.show()

