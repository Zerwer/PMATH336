import sys
import math
from copy import deepcopy
import numpy as np

class Group:
    def __init__(self, identity, elements, operator):
        self.identity = identity
        self.operator = operator

        if self.identity in elements:
            self.elements = elements
        else:
            self.elements = [self.identity] + elements

    # Latex

    def latex_create_table(self, rows, columns, op):
        sys.stdout.write('\\begin{tabular}{|' + 'c|' * (len(columns) + 1) + '}\n')
        sys.stdout.write('\\hline\n')
        sys.stdout.write('a/b & $' + '$ & $'.join([str(x) for x in columns]) + '$ \\\\\n')
        sys.stdout.write('\\hline\n')
        for y in rows:
            sys.stdout.write('$' + str(y) + '$ & $' + '$ & $'.join([op(y, x) for x in columns]) + '$ \\\\\n')
            sys.stdout.write('\\hline\n')
        sys.stdout.write('\\end{tabular}\n\n')
        sys.stdout.flush()

    def latex_operation_table(self):
        self.latex_create_table(self.elements, self.elements, lambda x,y: self.to_str(self.operator(x, y)))

    def latex_conjugation_table(self):
        op = lambda x, y: self.to_str(self.operator(self.operator(x, y), self.find_inverse(x)))
        self.latex_create_table(self.elements, self.elements, op)

    def latex_element_order(self):
        op = lambda x, _: str(self.order(x))
        self.latex_create_table(self.elements, ["Order"], op)

    def latex_number_of_each_order(self):
        order = {n: 0 for n in range(1, len(self.elements) + 1)}
        for x in self.elements:
            order[self.order(x)] += 1
        op = lambda x, _: str(order[x])
        r = [i for i in range(1, len(self.elements) + 1) if order[i] != 0]
        self.latex_create_table(r, ["Number"], op)

    # Solve X^mY^n = Z
    def latex_solve_power(self, m, n, Z):
        for x in self.elements:
            for y in self.elements:
                a = x
                for _ in range(m - 1):
                    a = self.operator(a, x)
                
                b = y
                for _ in range(n - 1):
                    b = self.operator(b, y)

                res = self.operator(a, b)

                if res == Z:
                    sys.stdout.write(f"${x}^{m}{y}^{n} = {Z}$, ")
        
        sys.stdout.write('\b\b\\\\\n\n')
        sys.stdout.flush()

    # Operations

    def find_inverse(self, x):
        for y in self.elements:
            if self.operator(x, y) == self.identity:
                return y

    def find_elements_of_order(self, n):
        return [x for x in self.elements if self.order(x) == n]

    def find_elements_func(self, func):
        return [x for x in self.elements if func(x)]

    def order(self, x):
        count = 1
        res = x
        while res != self.identity:
            res = self.operator(res, x)
            count += 1
        return count

    def left_coset_in(self, G):
        groups = []
        for a in G.elements:
            new_group = deepcopy(G)
            new_group.elements = [self.operator(a, x) for x in self.elements]
            groups.append((a, new_group))

        return groups
    
    def conjugate_subgroups_in(self, G):
        for a in G.all:
            yield G.to_str(a), Group(operator=G.operator, identity=G.identity, elements=[G.operator(G.operator(a, x), G.find_inverse(a)) for x in self.all])

    def normal_subgroup_of(self, G):
        for a in G.elements:
            for b in self.elements:
                res = G.operator(G.operator(a, b), G.find_inverse(a))
                
                if not any(x == res for x in self.elements):
                    return a, b

        return True

    # Operator overloads

    def __eq__(self, other):
        a_subset = all(x in other.elements for x in self.elements)
        b_subset = all(x in self.elements for x in other.elements)

        return a_subset and b_subset

    def __mul__(self, other):
        return CompositionGroup(self, other)

    # String

    def to_str(self, elem):
        return str(elem)
    
    def list_elements_str(self):
        return ', '.join([self.to_str(x) for x in self.elements])

class CompositionGroup(Group):
    def __init__(self, G, H):
        self.G = G
        self.H = H

        identity = (G.identity, H.identity)
        elements = [(x, y) for x in G.elements for y in H.elements]
        operator = lambda x, y: (G.operator(x[0], y[0]), H.operator(x[1], y[1]))
        super().__init__(identity, elements, operator)
    
    def to_str(self, elem):
        return f'({self.G.to_str(elem[0])}, {self.H.to_str(elem[1])})'

class AdditiveGroup(Group):
    def __init__(self, n):
        elements = [x for x in range(1, n)]
        op = lambda x, y: (x + y) % n
        super().__init__(0, elements, op)

class UnitModuloGroup(Group):
    def __init__(self, n):
        elements = [x for x in range(1, n) if math.gcd(x, n) == 1]
        op = lambda x, y: (x * y) % n
        super().__init__(1, elements, op)

class CyclicGroup(Group):
    def __init__(self, identity, generator, operator):
        elements = []
        res = generator
        while res not in elements:
            elements.append(res)
            res = operator(res, generator)

        super().__init__(identity, elements, operator)

class DihedralGroup(Group):
    def __init__(self, n):
        self.n = n
        elements =  ["I"] + [f"R_{x}" for x in range(1, n)] + [f"F_{x}" for x in range(0, n)]
        super().__init__("I", elements, self.operation)

    def operation(self, x, y):
        res = x
        if x == 'I':
            res = y
        elif x[0] == 'R' and y[0] == 'R':
            res = f'R_{(int(x[2]) + int(y[2])) % self.n}'
        elif x[0] == 'R' and y[0] == 'F':
            res = f'F_{(int(x[2]) + int(y[2])) % self.n}'
        elif x[0] == 'F' and y[0] == 'R':
            res = f'F_{(int(x[2]) - int(y[2])) % self.n}'
        elif x[0] == 'F' and y[0] == 'F':
            res = f'R_{(int(x[2]) - int(y[2])) % self.n}'

        if res == 'R_0':
            res = 'I'

        return res
    
class QuaternionGroup(Group):
    def __init__(self):
        identity = 'I'
        elements = ['I', 'A', 'B', 'C', '-I', '-A', '-B', '-C']
        operator = self.quaternion_multiplication
        super().__init__(identity, elements, operator)

class QuaternionGroup(Group):
    class Element:
        def __init__(self, M):
            self.M = M
            
            self.A = np.array([[0, 1], [-1, 0]])
            self.B = np.array([[0, 1j], [1j, 0]])
            self.C = np.array([[1j, 0], [0, -1j]])

        def __mul__(self, other):
            return self.M @ other.M

        def __eq__(self, other):
            return np.array_equal(self.M, other.M)
    
        def __str__(self):
            if np.array_equal(self.M, np.eye(2)):
                return 'I'
            elif np.array_equal(self.M, self.A):
                return 'A'
            elif np.array_equal(self.M, self.B):
                return 'B'
            elif np.array_equal(self.M, self.C):
                return 'C'
            elif np.array_equal(self.M, -np.eye(2)):
                return '-I'
            elif np.array_equal(self.M, -self.A):
                return '-A'
            elif np.array_equal(self.M, -self.B):
                return '-B'
            elif np.array_equal(self.M, -self.C):
                return '-C'

    def __init__(self):
        identity = self.Element(np.eye(2))
        A = np.array([[0, 1], [-1, 0]])
        B = np.array([[0, 1j], [1j, 0]])
        C = np.array([[1j, 0], [0, -1j]])
        elements = [identity, self.Element(A), self.Element(B), self.Element(C), self.Element(-np.eye(2)), self.Element(-A), self.Element(-B), self.Element(-C)]

        super().__init__(identity, elements, lambda x, y: self.Element(x * y))

