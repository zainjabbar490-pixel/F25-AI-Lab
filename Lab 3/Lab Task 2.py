
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': ['G'],
    'E': ['G'],
    'F': ['G'],
    'G': []
}

def dls(node, goal, limit, path, visited):
    visited.append(node)
    if node == goal:
        return path + [node], False
    if limit == 0:
        return None, True

    cutoff = False
    for child in graph[node]:
        if child not in path + [node]:
            result, cut = dls(
                child, goal, limit - 1,
                path + [node], visited
            )
            if result:
                return result, False
            cutoff = cutoff or cut
    return None, cutoff

for limit in range(1, 5):
    visited = []
    path, cut = dls('A', 'G', limit, [], visited)
    status = "FOUND" if path else "CUTOFF" if cut else "FAILURE"
    print(f"DLS Limit {limit}: {status}, Visited={visited}, Path={path}")

print("\nIDDFS:")
for depth in range(1, 5):
    visited = []
    path, cut = dls('A', 'G', depth, [], visited)
    print(f"Depth {depth}: Visited={visited}, Path={path}")
    if path:
        print("Goal FOUND at depth", depth)
        break
