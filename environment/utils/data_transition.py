class Delivery:
    def __init__(self, destination_id: int, destination_type: str, number_of_packets: int) -> None:
        self.destination_id = destination_id
        self.destination_type = destination_type
        self.number_of_packets = number_of_packets
        