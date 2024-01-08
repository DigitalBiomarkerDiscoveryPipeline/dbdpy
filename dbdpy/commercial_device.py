class CommercialDevice:
    def __init__(
        self,
        device_brand=None,
        device_model=None,
        energy=None,
        distance=None,
        oxygen=None,
        heart_rate=None,
    ) -> None:
        self.energy = energy
        self.distance = distance
        self.oxygen = oxygen
        self.heart_rate = heart_rate
