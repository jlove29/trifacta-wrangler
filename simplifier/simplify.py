import networkx as nx
import re
import numpy
import matplotlib.pyplot as plt
import pygraphviz
from networkx.drawing.nx_agraph import graphviz_layout

alllines = []
filename = "wscript.txt" 
file = open(filename, "r")
for line in file:
    alllines.append(line)

openColumns = []
fullEdgeList = []

# get operation of line
def getFirst(line):
    return(line.split(" ")[0])

# returns a list of parameters
def ops(line):
    a = line.split(" ")
    a = a[1:]
    newa = []
    for member in a:
        if ":" in member:
            member = "**"+member
        newa.append(member)
    b = ''.join(map(str, newa))
    e = b.split("**")
    e = e[1:]
    return e

# initialize graph
G = nx.DiGraph()

# get numbered node name from column name
def getNodeName(col):
    inCol = 0
    for node in openColumns:
        if col+"__" in node:
            num = node.split("__")[-1]
            return col+"__"+str(num)
            inCol = 1  
    if inCol == 0:
        return col+"__0"

# add node to flow, openColumns
def appendNode(col):
    searched = 0
    for node in openColumns:
        if col+"__" in node:
            openColumns.remove(node)
            num = node.split("__")
            newName = col+"__"+str(int(num[-1])+1)
            openColumns.append(newName)
            G.add_node(newName)
            searched = 1
    if searched == 0:
        newName = col+"__0"
        openColumns.append(newName)
        G.add_node(newName)

# link list of nodes to other list
def linkNode(sources, destinations, op):
    for source in sources:
        for dest in destinations:
            G.add_edge(source, dest)
            fullEdgeList.append([(source, dest), op])

# link node to column
def linkPrev(nodeName, op):
    allUsed = []
    for node in G.nodes():
        if nodeName in node:
            allUsed.append(node)
    prev = nodeName+"__"+str(len(allUsed)-1)
    current = nodeName+"__"+str(len(allUsed))
    linkNode([prev],[current], op) 
    if prev in openColumns:
        openColumns.remove(prev)
    if current not in openColumns:
        openColumns.append(current)

# break and return new nodes
def breakPattern(op):
    appendNode('breakTree')
    currentBreak = getNodeName('breakTree')
    openColumns.remove(currentBreak)
    linkNode(openColumns, [currentBreak], op)
    for node in G.nodes():
        if node in openColumns:
            column = node.split("__")[0]
    # have to brute-force adding the node to avoid duplication? not sure why
            newNode = getNodeName(column).split("__")[0]+"__"+str(int(getNodeName(column).split("__")[1])+1)
            G.add_node(newNode)
            openColumns.remove(node)
            openColumns.append(newNode)
    linkNode([currentBreak], openColumns, op)

# link column to dead node
def killColumn(cols, op):
    if "dead__" not in G.nodes():
        G.add_node("dead__")
    linkNode(cols, ["dead__"], op)
    for node in cols:
        if node in openColumns:
            openColumns.remove(node)

# aggregate operation
def aggregate(opslist):
    groupCols = []
    involvedNodes = []
    for op in opslist:
        op = op.split(":") 
# get aggregated column, rename based on function
        if op[0] == 'value':
            for word in op[1:]:
                c = word.split("(")
                func = c[0].lower()
                d = c[1].split(")")    
                valueCol = func+"_"+d[0]
                sourceCol = d[0]
                involvedNodes.append(getNodeName(valueCol))
                involvedNodes.append(getNodeName(sourceCol))
# get kept columns
        if op[0] == 'group':
            names = op[1].split(",")    
        # add all group nodes to newNames
            for node in names:
                node = node.replace("\n", "")
                appendNode(node)
                involvedNodes.append(getNodeName(node))
                groupCols.append(getNodeName(node))
# add groupColumns  
    appendNode(valueCol)
    linkNode(groupCols, [getNodeName(valueCol)], opslist)
    linkNode([getNodeName(sourceCol)], [getNodeName(valueCol)], opslist)
# kill remaining columns
    for node in openColumns:
        if node not in involvedNodes:
            killColumn([node], opslist)

# countpattern operation
def countpattern(opslist):
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
            newNode = "countPattern_"+op[1]
            appendNode(newNode)
            source = getNodeName(op[1])
            dest = getNodeName(newNode)
            linkNode([source], [dest], opslist)

# derive operation
def derive(opslist):
    print openColumns
    groupNames = []
    for op in opslist:
        op = op.split(":")
# deal with relevant columns, columnName
        if op[0] == 'as':
            columnName = op[1]
            columnName = columnName.replace("'", "")
            columnName = columnName.replace("\n", "")
        if op[0] == 'group':
            groupNames.append(op[1])
# get important columns    
        if op[0] == 'value':
            exp = op[1]
            exp1 = exp.split("(")[1].split(",")[0]
            exp2 = exp1.replace(">", " ").replace("<", " ").replace("=", " ")
            exp3 = exp2.split(" ")
            possibleCols = []
    # get things I think are names, not expressions
            for word in exp3:
                try:
                    float(word)
                except(ValueError):
                    fnsList = []
                    if word not in fnsList:
                        possibleCols.append(word) 
    # guess at words, and raise uncertainty error
            try:
                guess = possibleCols[0]
                if len(possibleCols) != 1:
                    print "Possible error on Derive operation"
            except IndexError:
                print "Error on Derive operation"
                breakPattern(opslist)
# add new column node, and link it to priors
    appendNode(columnName)
    groupTitles = []
    for name in groupNames:
        groupTitles.append(getNodeName(name))
    linkNode(groupTitles,[getNodeName(columnName)], opslist)    
    isIn = 0
    for node in openColumns:
        if guess+"__" in node:
            isIn = 1
    if isIn == 0:
        appendNode(guess)
    linkNode([getNodeName(guess)], [getNodeName(columnName)], opslist)

# drop column operation
def drop(opslist):
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
            columnName = op[1]
            columnName = columnName.replace("\n", "")
        if getNodeName(columnName) not in openColumns:
            appendNode(columnName)
        if "dead__" not in G.nodes():
            G.add_node("dead__")
        linkNode([getNodeName(columnName)], ["dead__"], opslist)

# extract operation
def extract(opslist):
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
# create new node from colname1
            appendNode(op[1]+"1")
            sourceNode = getNodeName(op[1])
            if sourceNode not in openColumns:
                appendNode(op[1])
            linkNode([sourceNode], [getNodeName(op[1]+"1")], opslist)
    
# create new branch with AS operation
def new_as(opslist):
# identify source and destination
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
            sourcecol = op[1]    
        if op[0] == 'as':
            destcol = op[1]
# remove ' characters
    destcol = destcol.replace("'", "")
    destcol = destcol.replace("\n", "")
# append destination, add to open columns
    appendNode(destcol)
    destcolName = getNodeName(destcol)
    openColumns.append(destcolName)
# check if source exists, add if not
    sourceExists = 0
    for node in openColumns:
        if sourcecol+"__" in node:
            sourceExists = 1
    if sourceExists == 0:
        appendNode(sourcecol) 
# get Node name of source    
    sourcecolName = getNodeName(sourcecol)
# add source to openColumns
    if sourcecolName not in openColumns:
        openColumns.append(sourcecolName)
# link nodes
    linkNode([sourcecolName], [destcolName], opslist) 

def merge(opslist):
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
# find out which columns are relevant
            actualColumns = []
            possibleColumns = op[1].split(",")
            for operand in possibleColumns:
                if operand[0] != "'":
                    actualColumns.append(operand) 
        if op[0] == 'as':
            destColumn = op[1].replace("'", "").replace("\n", "")
    appendNode(destColumn)
    acNames = []
    for node in actualColumns:
        acNames.append(getNodeName(node))
    linkNode(acNames, [getNodeName(destColumn)], opslist)
    for node in acNames:
        if node not in openColumns:
            openColumns.append(node)

for line in alllines:
    op = getFirst(line)

    openColumns = list(set(openColumns))

    if op == "aggregate":
        aggregate(ops(line))
        print "aggregated"

    if op == "countpattern":
        countpattern(ops(line))
        print "countpatterned"

    if op == "deduplicate\n":
        breakPattern("deduplicate")
        print "deduplicated"
    
    if op == "delete":
        breakPattern("delete")
        print "deleted"

    if op == "derive":
        derive(ops(line))
        print "derived"

    if op == "drop":
        drop(ops(line))
        print "dropped"

    if op == "extract":
        extract(ops(line))
        print "extracted"

    if op == "extractkv":
        new_as(ops(line))
        print "extractkvd"

    if op == "extractlist":
        new_as(ops(line))
        print "extracted list"

    if op == "flatten":
        breakPattern("flatten")
        print "flattened"

    if op == "keep":
        breakPattern("keep")
        print "kept"

    if op == "merge":
        merge(ops(line))
        print "merged"


colorList = []
nodeList = []
for node in openColumns:
    nodeList.append(node)
    colorList.append("red") 
for node in G.nodes():
    if node not in nodeList:
        nodeList.append(node)
        colorList.append("blue")

nx.draw(G, node_color=colorList, nodelist=nodeList, pos=graphviz_layout(G), with_labels=True)
plt.show()














