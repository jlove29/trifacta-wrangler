import ./util

# rename column operation
def rename(opslist):
    for op in opslist:
        op = op.split(":")
        if op[0] == 'col':
            sourceCol = op[1]
            sourceColName = util.getNodeName(op[1])
        if op[0] == 'as':
            destCol = op[1].replace("'", "").replace("\n", "")
            destColName = util.getNodeName(destCol)

   
    util.appendNode(destCol)
    util.killColumn([sourceColName], opslist)
    util.linkNode([sourceColName], [destColName], opslist)
