
def readFiles(): 
	lines = []
	scriptFile = "wscript.txt" 
	script = open(scriptFile, "r")
	for line in file:
	    lines.append(line)
	columns = []
	columnFile = "columns.txt"
	columnList = open(columnFile, "r")
	for line in columnList:
	    line = line.replace('\n', '').replace("'", "")
	    columns.append(line)
	return [lines, columns]