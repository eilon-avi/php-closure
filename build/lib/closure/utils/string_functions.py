import base64


def right_pad(s: str, multiple: int, char: str) -> str:
    return s.ljust(len(s) + (-len(s) % multiple), char)

def left_pad(s: str, multiple: int, char: str) -> str:
    return s.rjust(len(s) + (-len(s) % multiple), char)

def mult_3(s: str|bytes) -> bytes:
    if isinstance(s, str):
        s = s.encode()
    return s.decode('utf-16').encode('utf-8')

def prepare_injection_data(s: str) -> str:
    if len(s) % 4 != 0:
        raise RuntimeError("Something went wrong!")

    s = mult_3(s)
    s = mult_3(s)
    s = base64.b64encode(s).decode()

    return s.replace("=", "")
