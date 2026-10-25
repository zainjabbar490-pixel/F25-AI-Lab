import math
TREE = [
    [[3, 5], [6, 9]],
    [[1, 2], [0, -1]],
]
def minimax(node, maximizing, counter):
    if isinstance(node, int):
        counter["leaves"] += 1          # <-- leaf evaluation counter
        return node
    if maximizing:
        best = -math.inf
        for child in node:
            best = max(best, minimax(child, False, counter))
        return best
    best = math.inf
    for child in node:
        best = min(best, minimax(child, True, counter))
    return best
def alphabeta(node, maximizing, alpha, beta, counter):
    if isinstance(node, int):
        counter["leaves"] += 1          # <-- leaf evaluation counter
        return node
    if maximizing:
        best = -math.inf
        for child in node:
            best = max(best, alphabeta(child, False, alpha, beta, counter))
            alpha = max(alpha, best)
            if alpha >= beta:           # prune
                break
        return best
    best = math.inf
    for child in node:
        best = min(best, alphabeta(child, True, alpha, beta, counter))
        beta = min(beta, best)
        if alpha >= beta:               # prune
            break
    return best
if __name__ == "__main__":
    c_mm = {"leaves": 0}
    c_ab = {"leaves": 0}
    v_mm = minimax(TREE, True, c_mm)
    v_ab = alphabeta(TREE, True, -math.inf, math.inf, c_ab)

    print(f"Minimax    -> value = {v_mm}, leaves evaluated = {c_mm['leaves']}")
    print(f"Alpha-Beta -> value = {v_ab}, leaves evaluated = {c_ab['leaves']}")
    assert v_mm == v_ab, "Dono ki root value same honi chahiye!"
    print("Check passed: root values match.")