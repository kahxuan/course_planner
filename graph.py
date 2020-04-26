from node import UnitNode
from edge import Edge
from heap import Heap

class CourseGraph:

    def __init__(self, units, offers):

        self.cummulated_cp = 0
        self.unit_nodes = {}
        self.ready = [Heap(), Heap()]
        self.order = []
        
        self.set_units(units)
        self.set_offers(offers)
        self.set_priority()
        self.set_ready()


    def add_edge(self, from_node, to_node):
        new_edge = Edge(from_node, to_node)
        from_node.edges.append(new_edge)
        to_node.incoming_count += 1


    def assign_unit_node(self, unit): 
        self.unit_nodes[unit['code']] = UnitNode(
            unit['code'], 
            unit['credit_points'], 
            unit['req_point'])


    def set_unit_rule(self, unit):

        cur_unit_node = self.unit_nodes[unit['code']]
        
        for man_units in unit['prerequisite']:

            if len(man_units) == 1:
                if man_units[0] in self.unit_nodes:
                    self.add_edge(self.unit_nodes[man_units[0]], cur_unit_node)

            else:
                imd_node = UnitNode(None, 0, 0)
                for opt_unit in man_units:
                    if opt_unit in self.unit_nodes:
                        self.add_edge(self.unit_nodes[opt_unit], imd_node)
                imd_node.incoming_count = 1
                self.add_edge(imd_node, cur_unit_node)

        for pro_unit in unit['prohibition']:
            if pro_unit in self.unit_nodes:
                cur_unit_node.prohibiting_nodes.append(self.unit_nodes[pro_unit])
        

    def set_units(self, units):
        units.apply(self.assign_unit_node, axis=1)
        units.apply(self.set_unit_rule, axis=1)
        

    def set_offers(self, offers):
        f = lambda sem_no : lambda code: self.unit_nodes[code].offer_in(sem_no)
        offers[offers['period'] == 'First semester']['code'].apply(f(1))
        offers[offers['period'] == 'Second semester']['code'].apply(f(2))


    def _set_priority_aux(self, node, imd_nodes):
        if node.priority is None:
            node.priority = int(node.unit_code is not None)
            other_ends = node.get_other_ends()
            for other_end in other_ends:
                self._set_priority_aux(other_end, imd_nodes)
                node.priority += other_end.priority
            if node.unit_code is None:
                imd_nodes.append(node)


    def set_priority(self):
        ls = []
        imd_nodes = []

        for unit in self.unit_nodes:
            if self.unit_nodes[unit].is_req_met(self.cummulated_cp):
                ls.append(self.unit_nodes[unit])

        for node in ls:
            self._set_priority_aux(node, imd_nodes)

        for node in imd_nodes:
            node.offer = [1, 1]
            node.priority = 10e99


    def add_to_ready(self, node):
        for i in range(2):
            if node.is_offered(i + 1):
                self.ready[i].add(node)


    def set_ready(self):
        for unit in self.unit_nodes:
            if self.unit_nodes[unit].is_req_met(self.cummulated_cp):
                self.add_to_ready(self.unit_nodes[unit])


    def plan(self, start_sem):

        cur_sem = start_sem - 1

        while self.cummulated_cp < 144:

            cur_order = []

            for i in range(4):

                node = self.ready[cur_sem % 2].extract_max()

                if node is not None and node.offer[(cur_sem + 1) % 2] == 1:
                    self.ready[(cur_sem + 1) % 2].delete(node)

                cur_order.append(node)

            waiting_list = []

            for i in range(4):

                if cur_order[i] is not None:

                    self.cummulated_cp += cur_order[i].credit_point

                    for node in cur_order[i].prohibiting_nodes:
                        node.prohibited += 1

                    for node in cur_order[i].get_other_ends():
                        node.remove_incoming_edge()
                        waiting_list.append(node)

            for node in waiting_list:
                if node.is_req_met(self.cummulated_cp):
                    self.add_to_ready(node)

            while self.ready[cur_sem % 2].get_max() is not None and self.ready[cur_sem % 2].get_max().unit_code is None:
                imd_node = self.ready[cur_sem % 2].extract_max()
                self.ready[(cur_sem + 1) % 2].delete(node)
                for item in imd_node.get_other_ends():
                    item.remove_incoming_edge()
                    if item.is_req_met(self.cummulated_cp):
                        self.add_to_ready(item)

            self.order.append(cur_order)
            cur_sem += 1

        return self.order