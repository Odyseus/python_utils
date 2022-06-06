# -*- coding: utf-8 -*-
KBD_PATTERN = r"\[\[(?=\S)([\s\S]*?\S)\]\]"


def parse_kbd(inline, m, state):
    text = m.group(1)
    return "kbd_tag", inline.render(text, state)


def render_html_kbd(text):
    return "<kbd>" + text + "</kbd>"


def plugin_kbd(md):
    md.inline.register_rule("kbd_tag", KBD_PATTERN, parse_kbd)

    index = md.inline.rules.index("codespan")
    if index != -1:
        md.inline.rules.insert(index + 1, "kbd_tag")
    else:
        md.inline.rules.append("kbd_tag")

    if md.renderer.NAME == "html":
        md.renderer.register("kbd_tag", render_html_kbd)
