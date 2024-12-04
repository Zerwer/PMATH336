from typing import Any
from group import Group

class QuotientGroup(Group):
    class Element:
        def __init__(self, a, G):
            self.a = a
            self.G = G

        def add(self, a):
            self.a.append(a)

        def __eq__(self, other):
            return self.G == other.G
    
        def __str__(self):
            return self.G.to_str(self.a[0])

    def __init__(self, G, H):
        assert H.normal_subgroup_of(G)

        self.G = G
        self.H = H

        coset = H.left_coset_in(G)
        elements = []

        for a, G in coset:
            found = False
            for x in elements:
                if x == self.Element(a, G):
                    x.add(a)
                    found = True
            
            if not found:
                elements.append(self.Element([a], G))

        super().__init__(self.Element(G.identity, H), elements, self.operator)

    def operator(self, x, y):
        a = self.G.operator(x.a[0], y.a[0])
        for e in self.elements:
            if a in e.a:
                return e
