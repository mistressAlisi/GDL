import json
from colorama import Fore, Style, init
init(autoreset=True)

progress_state = {"tickets": 0, "target": None, "trials": 0}

def reset_progress(target=None):
    progress_state["tickets"] = 0
    progress_state["trials"] = 0
    progress_state["target"] = target

def colorize(msg):
    mtype = msg.get("type", "")
    if mtype == "ticket" or msg.get('ticket') is not None:
        # If wrapped message includes ticket key, show ticket
        progress_state["tickets"] += 1
        return (
            Fore.GREEN
            + f"[🎟️ Ticket {progress_state['tickets']}/{progress_state.get('target','?')}] "
            + json.dumps(msg, indent=2)
            + Style.RESET_ALL
        )
    elif mtype in ("warning", "skipped", "backoff", "progress"):
        progress_state["trials"] += 1
        return Fore.YELLOW + f"[⚠️ Trial {progress_state['trials']}] " + json.dumps(msg, indent=2) + Style.RESET_ALL
    elif mtype == "error":
        return Fore.RED + "[❌ ERROR] " + json.dumps(msg, indent=2) + Style.RESET_ALL
    elif mtype == "complete":
        return (
            Fore.CYAN
            + f"[✅ COMPLETE] Generated {progress_state['tickets']} tickets after {msg["trials"]} trials."
            + Style.RESET_ALL
        )
    return json.dumps(msg, indent=2)
