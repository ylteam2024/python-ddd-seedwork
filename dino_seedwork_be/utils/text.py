import base64


def censoredText(aText: str):
    if aText is None or len(aText.strip()) == 0:
        return aText

    return aText[0:2] + "******" + aText[-3:]


def parseNumOrKeeping(v: str):
    try:
        num = float(v)
        if num.is_integer():
            num = int(v)
        return num
    except Exception:
        return v


def split(v: str, sep: str):
    return v.split(sep)


def base64_to_string(b: bytes):
    return base64.b64decode(b).decode("utf-8")
