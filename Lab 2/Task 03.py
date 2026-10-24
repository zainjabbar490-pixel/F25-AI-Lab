LOW, HIGH = 18, 26

def control(temp, occupied, previous):
    if not occupied:
        target = "OFF"
    elif temp < LOW:
        target = "HEAT"
    elif temp > HIGH:
        target = "COOL"
    else:
        target = "OFF"

    command = target if target != previous else "NO COMMAND"
    return target, command

tests = [
    (15, True), (15, True), (18, True),
    (26, True), (30, True), (30, True),
    (10, False)
]

previous = "OFF"

print("Previous | Percept | Target | Command")

for temp, occupied in tests:
    target, command = control(temp, occupied, previous)
    print(previous, "|", (temp, occupied), "|",
          target, "|", command)
    previous = target