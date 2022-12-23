import base64

__all__ = ["censored_text", "parse_num_or_keeping", "split", "base64_to_string"]


def censored_text(a_text: str):
    if a_text is None or len(a_text.strip()) == 0:
        return a_text

    return a_text[0:2] + "******" + a_text[-3:]


def parse_num_or_keeping(v: str):
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
