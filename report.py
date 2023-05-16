##----[Imports]----##
import inspect
import datetime

##----[Logger]----##
class Logger:
	def __init__(self,modes={"i":"[INFO]", "w":"[WARNING]", "e": "[ERROR]"}):
		self.modes = modes
	
	def log(self,*args,mode=None):
		if mode == None:
			mode = next(iter(self.modes))
		final = ""
		final += self.modes[mode]
		final += " ["+self.getFnName()+"] "
		for a in args:
			final += str(a)
		print(final)
	
	def getFnName(self):
		return inspect.stack()[2][3]

logger = Logger()

##----[Functions]----##
def pester(string):
	inp = ""
	while not inp == "y" and not inp == "n":
		inp = input(string+"(y/n): ")
	if inp == "y":
		return True
	else:
		return False

#Modified for tuples - so the hashes are attached to values.
def quick_sort(inparray, low, high):
	if low < high:
		pivot = inparray[high][1]
		i = low - 1
		for j in range(low, high):
			if inparray[j][1] <= pivot:
				i = i + 1
				temp = inparray[j]
				inparray[j] = inparray[i]
				inparray[i] = temp
		temp  = inparray[high]
		inparray[high] = inparray[i+1]
		inparray[i+1] = temp
		quick_sort(inparray, low, i+1 - 1)
		quick_sort(inparray, i+1 + 1, high)
	return inparray

#Fibonnachi rehash. Original idea.
def findEmptyId(currId, table):
	newId = currId+currId #Assuming ids are sequential, attempt to prevent cascading rehash by doubling the id.
	fib1 = 1
	fib2 = 2
	while newId in table:
		newId += fib1
		fib2 += fib1
		fib1 = fib2 - fib1
	return newId

##----[Classes]----##
class Entry:
	def __init__(self,entryArray,datamask,labels):
		slicedLabels = labels[1:]
		self.dict = {}
		for i in range(len(datamask)):
			if i < len(entryArray):
				try:
					if datamask[i] == "int":
						self.dict[slicedLabels[i]] = int(entryArray[i])
					elif datamask[i] == "float":
						self.dict[slicedLabels[i]] = float(entryArray[i])
					elif datamask[i] == "date":
						self.dict[slicedLabels[i]] = datetime.datetime.strptime(entryArray[i], '%d.%m.%Y')
					else:
						self.dict[slicedLabels[i]] = entryArray[i]
				except ValueError:
					logger.log("Malformed data at column: ",slicedLabels[i],"; Using placeholder data.",mode='e')
					if datamask[i] == "int" or datamask[i] == "float":
						self.dict[slicedLabels[i]] = 0
					else:
						self.dict[slicedLabels[i]] = ""
			else:
				logger.log("Empty data at column: ",labels[i],"; Using placeholder data.",mode="w")
				if datamask[i] == "int" or datamask[i] == "float":
					self.dict[slicedLabels[i]] = 0
				else:
					self.dict[slicedLabels[i]] = ""

if __name__ == "__main__":
	##----[Preparations]----##
	
	#Inputs
	datamask = ["date","str","str","int","float","float"]
	filename = input("Input file?: ")
	if filename == "":
		logger.log("No file name provided. Defaulting to 'table.csv'",mode="w")
		filename = "table.csv"
	logger.log("Opening ",filename,"...")
	inpFile = open(filename,"r")
	lines = inpFile.readlines()
	firstIsLabels = pester("Use first line as labels?")
	
	logger.log("Processing contents...")
	
	#Figuring out labels
	labels = []
	for i in range(len(datamask)+1):
		firstLine = lines[0].split(';')
		firstLine[-1] = firstLine[-1].replace('\n',"")
		if firstIsLabels and i < len(firstLine):
			labels.append(firstLine[i])
		else:
			if not firstIsLabels:
				logger.log("Unnamed column. Failsafe name used: ",i,mode='e')
			labels.append(str(i))
	
	#Loading table itself
	table = {}
	isFirst = True
	for line in lines:
		line = line.replace("\n","")
		lineArr = line.split(";")
		
		#Skip first line, if it's labels
		if firstIsLabels and isFirst:
			isFirst = False
			continue
		
		entryHash = lineArr[0]
		try:
			entryHash = int(entryHash)
		except ValueError:
			logger.log("'",entryHash,"' is not a valid id. Rehashing...",mode='e')
			entryHash = findEmptyId(1,table)
			logger.log("Rehashed to: ",entryHash,mode='e')
		
		if entryHash in table:
			logger.log("Collision at id: ",entryHash,mode='w')
			entryHash = findEmptyId(entryHash,table)
			logger.log("Rehashed to: ",entryHash,mode='w')
		
		table[entryHash] = Entry(lineArr[1:],datamask=datamask,labels=labels)
	
	"""#Verify (debug)
	i=0
	print(labels)
	for key in table:
		i+=1
		if i > 10: #10 lines is enough
			break
		
		print(key,end=": ")
		entry = table[key]
		for column in entry.dict:
			value = entry.dict[column]
			print(value,end=", ")
		print("")
	"""
	
	#Overall profit. O(n)
	profit = 0
	for key in table:
		entry = table[key]
		profit += entry.dict['Общая стоимость']
	print("")
	logger.log("Overall profit is: ",profit)
	
	#Most sold product(s).
	array = []
	for key in table:
		entry = table[key]
		array.append((key,entry.dict['Количество продаж']))
	
	array = quick_sort(array,0,len(array)-1)
	
	print("")
	logger.log("Most sold:")
	timesSold = array[-1][1]
	logger.log(table[array[-1][0]].dict['Название товара']," : ",timesSold)
	sliceForReportSold = [(table[array[-1][0]].dict['Название товара'],timesSold)]
	if not len(array) < 2: # If for whatever reason we only have one entry, the following code will crash.
		i = 2
		nextBest = array[-i][1]
		while nextBest == timesSold:
			logger.log(table[array[-i][0]].dict['Название товара']," : ",timesSold)
			sliceForReportSold.append((table[array[-i][0]].dict['Название товара'],timesSold))
			i+=1
			if i >= len(array): # In case we somehow end up at the begining of the array
				break
			nextBest = array[-i][1]
	
	#Most profitable product(s).
	array = []
	for key in table:
		entry = table[key]
		array.append((key,entry.dict['Общая стоимость']))
	
	array = quick_sort(array,0,len(array)-1)
	
	print("")
	logger.log("Most profitable:")
	profitFromProduct = array[-1][1]
	logger.log(table[array[-1][0]].dict['Название товара']," : ",profitFromProduct)
	sliceForReportProfit = [(table[array[-1][0]].dict['Название товара'],profitFromProduct)]
	if not len(array) < 2: # If for whatever reason we only have one entry, the following code will crash.
		i = 2
		nextBest = array[-i][1]
		while nextBest == profitFromProduct:
			logger.log(table[array[-i][0]].dict['Название товара']," : ",profitFromProduct)
			sliceForReportProfit.append((table[array[-i][0]].dict['Название товара'],profitFromProduct))
			i+=1
			if i >= len(array): # In case we somehow end up at the begining of the array
				break
			nextBest = array[-i][1]
	
	#Constructing a .csv report
	array = []
	for key in table:
		entry = table[key]
		array.append((entry.dict['Название товара'],entry.dict['Количество продаж'],round(entry.dict['Общая стоимость']/profit*1000)/10))
	
	string = ""
	for elem in array:
		string = string + str(elem[0]) + ';' + str(elem[1]) + ';' + str(elem[2]) + '%\n'
	
	report = open("report.csv","w")
	lines = ["REPORT:\n","Overall Profit:;"+str(profit)+"\n","Name;Number sold;Percentage of profits\n",string]
	report.writelines(lines)
	print("")
	logger.log("report.csv created")