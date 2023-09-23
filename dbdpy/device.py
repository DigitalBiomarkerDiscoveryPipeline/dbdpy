class CommercialDevice:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def get_device_info(self):
        return f"{self.brand} - {self.model}"

    def calculate_rescale_value(self, age, is_damaged):
        initial_value = 1000
        depre_rate = 0.20 if self.brand == "Apple" else 0.15
        rescale_value = initial_value * ((1 - depre_rate) ** age)
        if is_damaged:
            rescale_value *= 0.70

        return round(rescale_value, 2)
