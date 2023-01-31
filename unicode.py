import keypirinha as kp
import keypirinha_util as kpu

import sys
import unicodedata

class Unicode(kp.Plugin):
    """Unicode character search"""

    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self._debug = False
        self.unicode_chars = {}

    def on_start(self):
        for ch in map(chr, range(sys.maxunicode+1)):
            name = unicodedata.name(ch, "").title()
            if name:
                item = self.create_item(
                    category=self.ITEMCAT_RESULT,
                    label="{}: {}".format(name, ch),
                    short_desc="Press ENTER to copy",
                    target=ch,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.KEEPALL,
                )
                self.unicode_chars[name] = item

        self.set_actions(self.ITEMCAT_RESULT, [
            self.create_action(
                name="copy",
                label="Copy",
                short_desc="Copy the character")])

    def on_catalog(self):
        self.set_catalog([self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label="Unicode:",
            short_desc="Search for Unicode characters",
            target="Unicode",
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.KEEPALL,
        )])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[-1].category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = [i for n,i in self.unicode_chars.items() if user_input.lower() in n.lower()]
        self.set_suggestions(suggestions[:10])

    def on_execute(self, item, action):
        kpu.set_clipboard(item.target())