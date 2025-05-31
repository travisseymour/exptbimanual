from typing import Optional, Self


class PropDict:
    """
    Dict like object that can also be accessed using dot-type property syntax.
    my_pd = PropDict()
    my_pd['one'] = 1
    my_pd.two = 2
    """

    def __init__(self, initial: Optional[dict] = None):
        # store everything in a private dict
        object.__setattr__(self, "_store", {})
        if initial:
            self._store.update(initial)

    def __getattr__(self, name: str):
        # attr access: return stored value or None
        return self._store.get(name, None)

    def __setattr__(self, name: str, value):
        # attr assignment: store into _store
        if name == "_store":
            object.__setattr__(self, name, value)
        else:
            self._store[name] = value

    def __getitem__(self, key: str):
        # dict‐style get
        return self._store.get(key, None)

    def __setitem__(self, key: str, value):
        # dict‐style set
        self._store[key] = value

    def __contains__(self, key: str):
        return key in self._store

    def __repr__(self) -> str:
        return str(self.to_dict())

    def get(self, key: str, default=None):
        return self._store.get(key, default)

    def to_dict(self):
        return dict(self._store)

    def combine(self, other: dict) -> Self:
        return PropDict(self.to_dict() | other)
