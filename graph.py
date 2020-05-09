from node import UnitNode
from edge import Edge
from heap import Heap

class CourseGraph:

    def __init__(self, units, offers, grad_req):

        self.cummulated_cp = 0
        self.unit_nodes = {}
        self.ready = [Heap(), Heap()]
        self.order = []
        self.wait_cp = [[] for _ in range(grad_req['credit_point'] // 6)]
        self.grad = False
        
        self.set_units(units)
        self.set_offers(offers)
        self.set_core(grad_req)
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


    def set_core(self, grad_req):
        grad_node = UnitNode('grad', 0, grad_req['credit_point'])
        for unit in grad_req['core']:
            self.unit_nodes[unit].priority_mult += 2
            for node in self.unit_nodes[unit].prohibiting_nodes:
                node.prohibited += 1

            self.add_edge(self.unit_nodes[unit], grad_node)


        elec_node = UnitNode(None, 0, 0)
        for unit in grad_req['elective']:
            self.unit_nodes[unit].priority_mult += 1
            self.add_edge(self.unit_nodes[unit], elec_node)
        elec_node.incoming_count = grad_req['elective_num']

        self.add_edge(elec_node, grad_node)

        grad_node.priority = 100
        self.unit_nodes['grad'] = grad_node
        self.unit_nodes['elec'] = elec_node


    def _set_priority_aux(self, node, imd_nodes):
        if node.priority is None:
            node.priority = int(node.unit_code is not None) * node.priority_mult
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
            if self.unit_nodes[unit].is_pp_req_met():
                ls.append(self.unit_nodes[unit])

        for node in ls:
            self._set_priority_aux(node, imd_nodes)

        for node in imd_nodes:
            node.offer = [1, 1]
            node.priority = 10e99


    def add_to_ready(self, node):
        if node.unit_code == 'grad':
            self.grad = True

        for i in range(2):
            if node.is_offered(i + 1):
                self.ready[i].add(node)


    def eval_req(self, node):
        if node.is_pp_req_met():
            if node.unit_code is None or node.get_req_point() <= self.cummulated_cp and not node.deleted:
                self.add_to_ready(node)
            else:
                self.wait_cp[(node.get_req_point() // 6) - 1].append(node)



    def set_ready(self):
        for unit in self.unit_nodes:
            self.eval_req(self.unit_nodes[unit])
            # if self.unit_nodes[unit].is_pp_req_met():
            #     self.add_to_ready(self.unit_nodes[unit])


    def plan(self, start_sem):

        cur_sem = start_sem - 1
        stucked = False
        while not self.grad and not stucked:

            cur_order = []

            stucked = False
            cur_sem_cp = 0
            while not stucked and cur_sem_cp < 24:

                node = self.ready[cur_sem % 2].extract_max()

                if node is not None:
                    cur_sem_cp += node.credit_point
                    if node.offer[(cur_sem + 1) % 2] == 1:
                        self.ready[(cur_sem + 1) % 2].delete(node)
                    cur_order.append(node)

                else:
                    stucked = True

            for i in range(self.cummulated_cp // 6, min((self.cummulated_cp + cur_sem_cp) // 6, len(self.wait_cp))):
                for node in self.wait_cp[i]:
                    self.add_to_ready(node)

            self.cummulated_cp += cur_sem_cp

            waiting_list = []

            for i in range(len(cur_order)):

                for node in cur_order[i].prohibiting_nodes:
                    node.prohibited += 1

                for node in cur_order[i].get_other_ends():
                    node.remove_incoming_edge()
                    waiting_list.append(node)


            for node in waiting_list:
                self.eval_req(node)

            m = self.ready[cur_sem % 2].get_max()

            while m is not None and (m.unit_code is None or m.unit_code == 'grad'):
                imd_node = self.ready[cur_sem % 2].extract_max() # TODO
                self.ready[(cur_sem + 1) % 2].delete(imd_node)
                for item in imd_node.get_other_ends():
                    item.remove_incoming_edge()
                    self.eval_req(item)

                m = self.ready[cur_sem % 2].get_max()

            self.order.append(cur_order)
            cur_sem += 1

        return self.order