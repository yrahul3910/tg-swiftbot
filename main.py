import re
from typing import Any, Generator

from acronyms import acronyms, taylorsVersions
from bot import TelegramBot


def get_response(msg: str, multi: bool) -> Generator[tuple[str, str | None], Any, None]:
    full = None  # Expanded form of the acronym
    detected = ""  # Acronym detected
    album = None
    for acronym in acronyms:
        pattern = r"\b{}\b".format(re.escape(acronym + "TV"))
        if re.search(pattern, msg, re.IGNORECASE):
            album = acronyms[acronym][1]
            if album in taylorsVersions:
                detected = acronym + "TV"
            else:
                detected = acronym

            if "Taylor's Version" not in acronyms[acronym][0] and acronyms[acronym][1] in taylorsVersions:
                if "(" in msg:
                    full = acronyms[acronym][0] + " [Taylor's Version]"
                else:
                    full = acronyms[acronym][0] + " (Taylor's Version)"
            else:
                full = acronyms[acronym][0]

            if multi:
                yield detected, full, album
                continue
            else:
                break

        pattern = r"\b{}\b".format(re.escape(acronym))
        if re.search(pattern, msg, re.IGNORECASE):
            detected = acronym
            full = acronyms[acronym][0]
            album = acronyms[acronym][1]

            if multi:
                yield detected, full, album
            else:
                break

    yield detected, full, album


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
            detected, full, album = entry
            if full is not None:
                reply += f"{list_formatter}{detected} can refer to: {full}, from {album}\n"

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
                # Print stack trace
                import traceback
                traceback.print_exc()
