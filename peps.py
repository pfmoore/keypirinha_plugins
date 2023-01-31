# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu

import json
from urllib.request import urlopen

class PEPs(kp.Plugin):
    """Python PEP search plugin"""

    KEYWORD = "peps"

    ITEMCAT_PEP = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        with urlopen("https://peps.python.org/api/peps.json") as f:
            data = json.load(f)
        self.PEPs = [(int(k), v["title"]) for k, v in data.items()]

        self.set_actions(self.ITEMCAT_PEP, [
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
        self.set_catalog([self.create_item(
            category=kp.ItemCategory.KEYWORD,
            target=self.KEYWORD,
            label="Python PEPs...",
            short_desc="Python Enhancement Proposals",
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.NOARGS,
        )])

    def on_suggest(self, user_input, items_chain):
        # Not yet selected our item, and no user input.
        if not items_chain and len(user_input) == 0:
            return
        # The chain doesn't start with us.
        if items_chain and (
                items_chain[0].category() != kp.ItemCategory.KEYWORD or
                items_chain[0].target() != self.KEYWORD):
            return

        # Otherwise, items_chain will be a 1-element list containing our "Python PEPs..." item

        suggestions = []
        for num, desc in self.PEPs:
            item_label = "PEP {}: {}".format(num, desc)

            match_score = 1
            if len(user_input) > 0:
                if items_chain and items_chain[0]:
                    against = item_label
                else:
                    against = self.item_label + " " + item_label
                match_score = kpu.fuzzy_score(user_input, against)

            if match_score:
                suggestion = self.create_item(
                    category=self.ITEMCAT_PEP,
                    label=item_label,
                    short_desc=desc,
                    target="https://www.python.org/dev/peps/pep-{:04d}/".format(num),
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.KEEPALL,
                )
                suggestions.append(suggestion)

        if len(suggestions) > 0:
            self.set_suggestions(suggestions)

    def on_execute(self, item, action):
        self.dbg(action.name() if action else "No action")
        self.dbg(item.category() if item else "No item")
        if item and item.category() == self.ITEMCAT_PEP:
            if action and action.name() == "copy":
                kpu.set_clipboard(item.target())
            elif action and action.name() == "copy_md":
                link = "[{}]({})".format(item.label().split(":", maxsplit=1)[0], item.target())
                kpu.set_clipboard(link)
            else:
                self.dbg("Launching", item.target())
                kpu.web_browser_command(url=item.target(), execute=True)
