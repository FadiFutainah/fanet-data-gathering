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

    def clear(self):
        self.data.clear()
