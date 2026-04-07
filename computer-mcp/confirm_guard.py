class ConfirmationDenied(Exception):
    pass


def request_confirm(action_description: str) -> dict:
    """
    Print the action to console and wait for user input.
    Raises ConfirmationDenied if user types anything other than 'y' / 'yes'.
    """
    print(f"\n[computer-mcp] HIGH-RISK ACTION: {action_description}")
    answer = input("Confirm? (y/n): ").strip().lower()
    if answer in ("y", "yes"):
        return {"confirmed": True, "action": action_description}
    raise ConfirmationDenied(f"User denied: {action_description}")
