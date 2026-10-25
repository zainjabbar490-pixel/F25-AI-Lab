g = {'S':[('A',1),('B',4)], 'A':[('C',2),('G',7)],
     'B':[('G',3)], 'C':[('G',3)], 'G':[]}
h = {'S':5,'A':4,'B':3,'C':2,'G':0}
front = [(5,0,'S')]

for i in range(3):
    front.sort()
    f,c,n = front.pop(0)
    print(n, "g=",c,"h=",h[n],"f=",f)
    for v,w in g[n]:
        front.append((c+w+h[v],c+w,v))
    print("Frontier:", front)