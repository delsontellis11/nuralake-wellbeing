import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.graph import run_agent

print("=" * 50)
print("Well Beings AI Agent — Local Test")
print("Type 'quit' to exit")
print("=" * 50)

history = []
phone = "+971501234567"

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() == "quit":
        break
    response = run_agent(user_input, phone, history)
    print(f"\nAgent: {response}")