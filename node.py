class UnitNode():

    def __init__(self, unit_code, credit_point, req_point):
        self.unit_code = unit_code
        self.credit_point = credit_point
        self.req_point = req_point
        self.offer = [0, 0]

        self.edges = []
        self.prohibiting_nodes = []

        self.priority = None
        self.priority_mult = 0.5
        self.incoming_count = 0
        self.prohibited = 0

        self.deleted = False
    
    def __str__(self):
        if self.unit_code is None:
            return 'node to' + str([edge.to_node.__str__() for edge in self.edges])
        return self.unit_code

    def get_other_ends(self):
        return [edge.to_node for edge in self.edges]


    def offer_in(self, sem):
        self.offer[sem - 1] = 1


    def is_offered(self, sem):
        return self.offer[sem - 1] == 1


    def is_pp_req_met(self):
        return self.prohibited <= 0 and \
            self.incoming_count <= 0

    def get_req_point(self):
        return self.req_point

    def remove_incoming_edge(self):
        self.incoming_count -= 1

    def print_full(self):
        print("------", self.unit_code, '------')
        if self.unit_code is None:
            print('node to' + str([edge.to_node.__str__() for edge in self.edges]))
        print(self.credit_point)
        print(self.req_point)
        print(self.offer)
        print(len(self.edges))
        print(self.prohibiting_nodes)
        print(self.priority)
        print(self.incoming_count)
        print(self.prohibited)
        print(self.is_pp_req_met())
        print(self.deleted)
        print('---------------------')