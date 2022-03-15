from glob import glob
import re
from collections import defaultdict, Counter
from math import log
import matplotlib.pyplot as plt

paths = sorted(glob("CODATA/allascii_*.txt"))

allyears = [int(path.split(".")[0].split("_")[-1]) for path in paths]

print(allyears)

lastyear = max(allyears)
firstyear = min(allyears)
rng = lastyear - firstyear

def cleanValue(value):
	"""Removes superfluous spaces and ellipses from values"""
	return value.strip().replace(" ", "").replace("...", "")

def splitUncertainty(value):
	"""Splits a constant that may contain parentheses uncertainty notation into its value and uncertainty value"""

	value = cleanValue(value)

	# Remove uncertainty parentheses to obtain the pure average value
	purevalue = re.sub(r"\(.*?\)", "", value)
	
	# Match the digits within parentheses
	rematch = re.search(r"\((.*?)\)", value)

	# Set pureuncertainty to these digits, or if there are none, to None
	pureuncertainty = rematch.group(1) if rematch else None
	
	if pureuncertainty:
		# Reconstruct the uncertainty value by inserting the right number of decimal zeros (assuming uncertainty < 1)
		pureuncertainty = "0." + "0" * (value.index("(") - value.index(".") - 1 - len(pureuncertainty)) + pureuncertainty
		
		# Also append the exponent notation of the purevalue to the uncertainty if there is any
		if "e" in purevalue:
			pureuncertainty += purevalue[purevalue.index("e"):]

	return purevalue, pureuncertainty

# {<name:str>: [<year:str>, <value:str>, <uncertainty:str/None>, <unit:str/None>]}
data = defaultdict(list)

# Iterate over all files and collect year-tagged datapoints in a list for each constant
for path in paths:

	# Extract the year as an integer
	year = int(path.split(".")[0].split("_")[-1])

	# Read all lines from the CODATA file into a list
	with open(path) as f:
		lines = f.read().splitlines()
	
	start = False
	for line in lines:
		
		# Ignore all lines in the file until the dashes, after which the constants follow
		if line.startswith("---"):
			start = True
			continue
		
		if not start:
			continue
		
		# Split the line between 2 or more whitespaces
		line = re.split(r"\s{2,}", line.strip())
		
		# Depending on the format of the CODATA file and available data each line may have a different number of columns
		if len(line) == 2:
			# Old format containing the uncertainty as parentheses notation in the value, no unit (dimensionless)
			name, value = line
			unit = None
			value, uncertainty = splitUncertainty(value)
		elif len(line) == 3:
			# Old format containing the uncertainty as parentheses notation in the value
			name, value, unit = line
			value, uncertainty = splitUncertainty(value)
		elif len(line) == 4:
			# New format (2010+) containing the uncertainty in a separate column
			name, value, uncertainty, unit = line
		else:
			# Shouldn't occur, doesn't currently
			print(line)
		
		value = cleanValue(value)
		if uncertainty:
			uncertainty = cleanValue(uncertainty)
		
		data[name].append([str(year), value, uncertainty, unit])

testkey = "electron mass"
print(testkey)
for year in data[testkey]:
	print("\t\t".join(year))

def isfloat(v):
	"""Returns True if the given value can be converted to a floating point number"""
	try:
		float(v)
		return True
	except ValueError:
		pass
	return False

for name, years in data.items():
	# Only plot constants for which data is available for all years
	if len(years) == len(allyears) and all([year[2] is not None and isfloat(year[2]) and float(year[2]) != 0 for year in years]):
		
		# Skip some redundant or uninteresting constants
		if " in " in name or " relationship" in name or " equivalent" in name or "atomic unit" in name or "molar " in name:
			continue
		
		# Collect x and y values for the plot
		xs = []
		ys = []
		for year in years:
			xs.append(int(year[0]))
			ys.append(log(float(years[0][2])/float(year[2]), 10))
		
		# Plot the constants' line
		plt.plot(xs, ys, label=name)
		
		# Additionally, print some information
		decimaldigits = log(float(years[0][2])/float(years[-1][2]), 10)
		if decimaldigits == 0:
			continue
		print(name)
		print("%.2f digits" % decimaldigits, "%.2f years/digit" % (rng/decimaldigits))

# Finish, save and show the plot
plt.title(f"number of decimal digits improved compared to first year ({firstyear}-{lastyear})")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.tight_layout()
plt.savefig("plot.png")
plt.show()

