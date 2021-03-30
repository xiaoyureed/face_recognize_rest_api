import hashlib


def md5(target: str) -> str:
    """md5 encryption
    """
    md5_hash_obj = hashlib.md5()
    md5_hash_obj.update(target.encode("utf-8"))
    return md5_hash_obj.hexdigest()
