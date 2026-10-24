systems = {
    "Delivery Robot": [
        "Partially Observable",
        "Hidden obstacles may exist.",
        "Stochastic",
        "Pedestrians may move unpredictably."
    ],
    "Student Support Agent": [
        "Partially Observable",
        "Student knowledge is not fully observable.",
        "Stochastic",
        "LLM responses may vary."
    ]
}

for name, details in systems.items():
    print("\n" + name)
    print("Observability:", details[0])
    print("Example:", details[1])
    print("Environment:", details[2])
    print("Example:", details[3])

print("\nSIMULATOR")
print("Fully observable if the complete state is visible.")
print("Deterministic if fixed rules give predictable outcomes.")