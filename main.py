from typing import Any, Generator
from bot import TelegramBot
from acronyms import acronyms


def get_response(msg: str, multi: bool) -> Generator[tuple[str, str | None], Any, None]:
    full = None  # Expanded form of the acronym
    detected = ""  # Acronym detected
    for acronym in acronyms:
        if acronym + "TV" in msg.upper():
            detected = acronym + "TV"

            if "Taylor's Version" not in acronyms[acronym]:
                if "(" in msg:
                    full = acronyms[acronym] + " [Taylor's Version]"
                else:
                    full = acronyms[acronym] + " (Taylor's Version)"
            else:
                full = acronyms[acronym]
            
            if multi:
                yield detected, full
                continue
            else:
                break
        
        if acronym in msg.upper():
            detected = acronym
            full = acronyms[acronym]

            if multi:
                yield detected, full
            else:
                break
    
    yield detected, full


def make_reply(msg: str) -> str | None:
    if "/nobot" in msg:
        return None

    # Match all acronyms?
    multi = False
    list_formatter = ""
    if "/multi" in msg:
        multi = True
        list_formatter = "- "

    full = None
    if msg is not None:
        entries = list(get_response(msg, multi))

        # Dedup entries
        entries = list(set(entries))

        # Compose reply message
        reply = ""
        for entry in entries:
            detected, full = entry
            if full is not None:
                reply += f"{list_formatter}{detected} can refer to: {full}\n"
        
        return None if reply == "" else reply

    return None


bot = TelegramBot('config.cfg')
print("Server started.")

update_id = None
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            print(item)
            update_id = item["update_id"]
            try:
                message = item["message"]
                message = str(item["message"]["text"])
                from_ = item["message"]["chat"]["id"]

                reply = make_reply(message)

                if reply is not None:
                    bot.send_message(reply, from_)
            except Exception as e:
                print(f"Failed, item = {item}: {e}")