
def check(score, completeness, citations, reliable):
    return score >= 70 and completeness >= 80 and citations and reliable

tests = [
    (70, 80, True, True),
    (85, 90, False, True),
    (85, 90, True, False),
    (69, 90, True, True)
]

for i, test in enumerate(tests, 1):
    print("Case", i, ":", "PASS" if check(*test) else "FAIL")
