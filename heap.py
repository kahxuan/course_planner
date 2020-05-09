class Heap:
    def __init__(self):
        self.array = [None]

    def __str__(self):
        ls = []
        for i in range(1, len(self.array)):
            ls.append(self.array[i].__str__() + " " + str(self.array[i].priority) )
            if self.array[i].deleted:
                ls[-1] += "(DELETED)"
        return str(ls)

    def is_empty(self):
        return self.get_count() == 0


    def get_count(self):
        return len(self.array) - 1


    def add(self, elem):
        # elem.deleted = False
        self.array.append(elem)
        self.rise(self.get_count())


    def delete(self, elem):
        elem.deleted = True


    def swap(self, i, j):
        self.array[i], self.array[j] = self.array[j], self.array[i]


    def get_largest_child(self, node):
        if 2 * node == self.get_count() or self.array[2 * node].priority > self.array[2 * node + 1].priority:
            return 2 * node
        return 2 * node + 1


    def rise(self, node):
        while node > 1 and self.array[node].priority > self.array[node // 2].priority:
            self.swap(node, node // 2)
            node = node // 2


    def sink(self, node):
        while 2 * node <= self.get_count():
            child = self.get_largest_child(node)
            if self.array[child].priority < self.array[node].priority:
                return
            self.swap(child, node)
            node = child


    def _extract_max_aux(self):
        if self.get_count() == 0:
            return None
        retval = self.array[1]
        self.swap(1, -1)
        self.array.pop()
        self.sink(1)
        return retval


    def extract_max(self):
        retval = self._extract_max_aux()

        while retval is not None  and retval.deleted:
            retval = self._extract_max_aux()
        if retval is not None:
            retval.deleted = True

        return retval
        
    def get_max(self):
        while self.get_count() > 0 and self.array[1].deleted:
            self._extract_max_aux()

        if self.get_count() == 0:
            return None
        else:
            return self.array[1]
