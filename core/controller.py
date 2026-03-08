from ai_engine import handle_command

print("=== KapiOS / PiSecOS AEGIS Console ===")

while True:

    cmd = input("AEGIS> ")

    if cmd == "exit":
        break

    handle_command(cmd)
