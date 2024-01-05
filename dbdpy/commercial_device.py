class CommercialDevice:
    def __init__(
        self,
        sleep=None,
        energy=None,
        steps=None,
        distance=None,
        oxygen=None,
        heart_rate=None,
    ) -> None:
        self.sleep = sleep
        self.energy = energy
        self.steps = steps
        self.distance = distance
        self.oxygen = oxygen
        self.heart_rate = heart_rate
