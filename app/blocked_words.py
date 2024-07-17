from config import config

def has_blocked_words(string: str) -> bool:
    lst = config.data["blocked_words"]

    for word in lst:
        if word in string:
            return True
    return False

def blocked_words_filter(string: str) -> str:
    lst = config.data["blocked_words"]
    method = config.data["blocked_words_deal_method"]

    ret = string
    if method == "ignore":
        ret = string
    elif method == "remove":
        for word in lst:
            ret = ret.replace(word, "")
    elif method == "replace":
        for word in lst:
            ret = ret.replace(word, config.data["blocked_words_replacement"])
    elif method == "skip":
        if has_blocked_words(string):
            ret = ""
    return ret