#summary[depth][num]

o = 6
max_depth = 4
depth = 0
# dfs = read_csv()
# head = blockno.max
# top = head - o + 1
# curr = top

def summarize(dfs, curr, l, depth):
    # Remove duplicate value from even pairs summary[depth-1][curr] to summary[depth-1][curr+l]


for l in [2,5,8,10,12,15,20,30,40,50,75,100,150,200,300,400]:
    depth = 0
    while (depth < max_depth):
        curr = top - pow(l,depth)
        top = curr
        depth = depth + 1
        while curr > blockno.min:
            curr = curr - pow(l,depth)
            summarize(dfs,curr,l,depth)