
from collections import deque

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': ['G'],
    'E': ['G'],
    'F': ['G'],
    'G': []
}

def bfs(start, goal):
    q = deque([(start, [start])])
    visited = []
    while q:
        node, path = q.popleft()
        if node in visited:
            continue
        visited.append(node)
        if node == goal:
            return visited, path
        for n in graph[node]:
            q.append((n, path + [n]))
    return visited, None

def dfs(node, goal, path=None, visited=None):
    if path is None:
        path = []
    if visited is None:
        visited = []
    visited.append(node)
    path = path + [node]
    if node == goal:
        return visited, path
    for n in graph[node]:
        if n not in visited:
            result = dfs(n, goal, path, visited)
            if result[1]:
                return result
    return visited, None

print("BFS:", bfs('A', 'G'))
print("DFS:", dfs('A', 'G'))
