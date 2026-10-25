import math
TREE = [
    [[3, 5], [6, 9]],
    [[1, 2], [0, -1]],
]
def minimax(node, maximizing, depth=0):
    indent = "  " * depth
    if isinstance(node, int):          # terminal node
        print(f"{indent}leaf = {node}")
        return node

    print(f"{indent}{'MAX' if maximizing else 'MIN'} node")
    if maximizing:
        best = -math.inf
        for child in node:
            best = max(best, minimax(child, False, depth + 1))
    else:
        best = math.inf
        for child in node:
            best = min(best, minimax(child, True, depth + 1))
    print(f"{indent}-> {'MAX' if maximizing else 'MIN'} returns {best}")
    return best
if __name__ == "__main__":
    result = minimax(TREE, True)
    print("\nRoot (Minimax) value =", result)