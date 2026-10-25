import math
import copy

TREE = [
    [[3, 5], [6, 9]],
    [[1, 2], [0, -1]],
]


def minimax(node, maximizing, counter):
    if isinstance(node, int):
        counter["leaves"] += 1
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
        counter["leaves"] += 1
        return node
    if maximizing:
        best = -math.inf
        for child in node:
            best = max(best, alphabeta(child, False, alpha, beta, counter))
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best
    best = math.inf
    for child in node:
        best = min(best, alphabeta(child, True, alpha, beta, counter))
        beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def value_of(node, maximizing):
    return minimax(node, maximizing, {"leaves": 0})


def reorder(node, maximizing, mode):
    """Har level par children ka order badalta hai (value change nahi hoti).
    mode: original | reversed | best_first | worst_first
    """
    if isinstance(node, int):
        return node
    kids = [reorder(c, not maximizing, mode) for c in node]
    if mode == "reversed":
        kids.reverse()
    elif mode in ("best_first", "worst_first"):
        desc = maximizing                 # MAX: bada pehle = best
        if mode == "worst_first":
            desc = not desc
        kids.sort(key=lambda c: value_of(c, not maximizing), reverse=desc)
    return kids


if __name__ == "__main__":
    print(f"{'Ordering':<13}{'MM value':>9}{'MM leaves':>11}{'AB value':>10}{'AB leaves':>11}")
    for mode in ("original", "reversed", "best_first", "worst_first"):
        t = reorder(copy.deepcopy(TREE), True, mode)
        c1, c2 = {"leaves": 0}, {"leaves": 0}
        v1 = minimax(t, True, c1)
        v2 = alphabeta(t, True, -math.inf, math.inf, c2)
        assert v1 == v2
        print(f"{mode:<13}{v1:>9}{c1['leaves']:>11}{v2:>10}{c2['leaves']:>11}")
        print(f"   tree: {t}")
    print("\nObservation: value har ordering mein same; Alpha-Beta ke leaves ordering par depend karte hain.")