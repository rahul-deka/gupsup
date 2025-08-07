def main():
    print("Welcome to TerminalChat")
    choice = input("Enter code to join or type 'new' to create a channel: ").strip()
    if choice.lower() == "new":
        from .client import create_channel
        create_channel()
    else:
        from .client import join_channel
        join_channel(choice)