from heapq import heappush, heappop


class PriorityQueue:
    def __init__(self):
        self.data = []

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def push(self, item):
        heappush(self.data, item)

    def pop(self):
        if not self.data:
            raise IndexError("Priority queue is empty.")
        return heappop(self.data)

    def get_item(self):
        return self.data[0]

    def clear(self):
        self.data.clear()

    def has_item(self, item) -> bool:
        for i in self.data:
            if i == item:
                return True
        return False

    def is_empty(self):
        return len(self.data) == 0
