class Storage:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Storage, cls).__new__(cls)
        return cls._instance
