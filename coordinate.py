from dataclasses import dataclass


@dataclass
class Coordinate:
    latitude: float
    longitude: float

    def to_tuple(self) -> tuple[float, float]:
        """
        Return a tuple of latitude and longitude in this order.

        There are no preconditions to use this method.
        """
        return self.latitude, self.longitude
