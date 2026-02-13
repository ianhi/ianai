"""Quick test to verify /model command parsing"""

test_inputs = [
    "/model",
    " /model",
    "/model ",
    " /model ",
    "/MODEL",
    "/Model",
]

for test in test_inputs:
    result = test.strip().lower() == "/model"
    print(f"Input: '{test}' -> strip().lower() == '/model': {result}")
