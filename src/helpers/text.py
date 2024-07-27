import re


class REGS:
    TAGS = re.compile("<*?>", re.S + re.A)


def strip_tag(html: str):
    return REGS.TAGS.sub("", html)
