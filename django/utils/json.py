from collections.abc import Mapping, Sequence


def normalize_json(obj):
    """Recursively normalize an object into JSON-compatible types."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported value: {type(obj)}")
    if type(obj) is dict:
        return {normalize_json(k): normalize_json(v) for k, v in obj.items()}
    if isinstance(obj, Mapping):
        return {normalize_json(k): normalize_json(v) for k, v in obj.items()}
    if type(obj) is list:
        return [normalize_json(v) for v in obj]
    if type(obj) is tuple:
        return [normalize_json(v) for v in obj]
    if isinstance(obj, Sequence):
        return [normalize_json(v) for v in obj]
    raise TypeError(f"Unsupported type: {type(obj)}")
