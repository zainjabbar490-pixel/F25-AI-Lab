import heapq

g = {'S':[('A',1),('B',4)], 'A':[('C',2),('G',7)],
     'B':[('G',3)], 'C':[('G',3)], 'G':[]}
h = {'S':5,'A':4,'B':3,'C':2,'G':0}

def search(H):
    q=[(H['S'],0,'S',['S'])]
    seen=set()
    while q:
        f,c,n,p=heapq.heappop(q)
        if n in seen: continue
        seen.add(n)
        if n=='G': return p,c,seen
        for v,w in g[n]:
            if v not in seen:
                heapq.heappush(q,(c+w+H[v],c+w,v,p+[v]))
    return None

print("A*:",search(h))
print("UCS:",search({n:0 for n in h}))