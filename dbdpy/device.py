class CommercialDevice:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def get_device_info(self):
        return f"{self.brand} - {self.model}"

    def whatthe(self):
        print("Whathe")
