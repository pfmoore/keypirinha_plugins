# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu

from collections import namedtuple
import json
import datetime
import os
from urllib.request import urlopen

class PEPs(kp.Plugin):
    """Python PEP search plugin"""

    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        with urlopen("https://peps.python.org/api/peps.json") as f:
            data = json.load(f)
        self.PEPs = [(int(k), v["title"]) for k, v in data.items()]

        self.set_actions(self.ITEMCAT_RESULT, [
            self.create_action(
                name="open",
                label="Open",
                short_desc="Open the PEP in a browser"),
            self.create_action(
                name="copy",
                label="Copy URL",
                short_desc="Copy the URL of the PEP"),
            self.create_action(
                name="copy_md",
                label="Copy as Markdown",
                short_desc="Copy a Markdown link to the URL")])


    def on_catalog(self):
         self.set_catalog([
            self.create_item(
                category=self.ITEMCAT_RESULT,
                label="PEP {}: {}".format(num, desc),
                short_desc=desc,
                target="https://www.python.org/dev/peps/pep-{:04d}/".format(num),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.KEEPALL,
            )
            for num, desc in self.PEPs
        ])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[-1].category() != kp.ItemCategory.KEYWORD:
            return

    def on_execute(self, item, action):
        self.dbg(action.name() if action else "No action")
        self.dbg(item.category() if item else "No item")
        if item and item.category() == self.ITEMCAT_RESULT:
            if action and action.name() == "copy":
                kpu.set_clipboard(item.target())
            elif action and action.name() == "copy_md":
                link = "[{}]({})".format(item.label().split(":", maxsplit=1)[0], item.target())
                kpu.set_clipboard(link)
            else:
                self.dbg("Launching", item.target())
                kpu.web_browser_command(url=item.target(), execute=True)
