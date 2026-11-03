import random

EVENT_TYPES = ["view_product", "add_to_cart", "remove_from_cart",
               "begin_checkout", "purchase"]

class UserSimulator:
    """Simple probabilistic journey model; probabilities are configurable later."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_journey(self):
        # At least one product view per session.
        journey = ["view_product"]
        # Browsing may continue across multiple products.
        for _ in range(self.rng.randint(0, 3)):
            if self.rng.random() < 0.65:
                journey.append("view_product")

        # Cart conversion and checkout are conditional, not independent events.
        if self.rng.random() < 0.35:
            journey.append("add_to_cart")
            if self.rng.random() < 0.12:
                journey.append("remove_from_cart")
                return journey
            if self.rng.random() < 0.55:
                journey.append("begin_checkout")
                if self.rng.random() < 0.65:
                    journey.append("purchase")
        return journey
