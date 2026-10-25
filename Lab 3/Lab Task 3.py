
import heapq
from collections import deque

g = {'A':[('B',1),('C',4)], 'B':[('D',2),('E',5),('C',4)],
     'C':[('F',1)], 'D':[('G',8)], 'E':[('G',1)],
     'F':[('G',3)], 'G':[]}

def ucs():
    q, seen = [(0,'A',['A'])], set()
    while q:
        c,n,p = heapq.heappop(q)
        if n in seen: continue
        seen.add(n)
        if n == 'G': return p,c
        for v,w in g[n]:
            heapq.heappush(q,(c+w,v,p+[v]))

def bfs():
    q = deque([('A',['A'])])
    seen = {'A'}
    while q:
        n,p = q.popleft()
        if n == 'G':
            cost = sum(next(w for v,w in g[a] if v==b)
                       for a,b in zip(p,p[1:]))
            return p,cost
        for v,w in g[n]:
            if v not in seen:
                seen.add(v)
                q.append((v,p+[v]))

print("UCS:", ucs())
print("BFS:", bfs())
