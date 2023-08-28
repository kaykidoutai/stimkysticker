class StimkyStickerException(Exception):
    def __init__(self, message: str):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
