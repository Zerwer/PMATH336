from itertools import permutations
from typing import Any
from group import Group
import math
from functools import reduce

class SymmetricGroup(Group):
    class Element(dict):
        def __init__(self, d):
            super().__init__(d)
            self.d = d

        def __eq__(self, other):
            if not isinstance(other, dict):
                raise NotImplementedError
            return all(self.get(k) == other.get(k) for k in self.keys())

    def __init__(self, n):
        self.n = n
        elements = [self.Element({i: p[i - 1] for i in range(1, n + 1)}) for p in permutations(range(1, n + 1))]

        super().__init__(
            self.Element({i: i for i in range(1, n + 1)}), 
            elements, 
            lambda x, y: self.Element({k: x[y[k]] for k in x.keys()}))

    def __eq__(self, other):
        a_subset = all(any(x == y for y in other.elements) for x in self.elements)
        b_subset = all(any(x == y for y in self.elements) for x in other.elements)

        return a_subset and b_subset
    
    def to_str(self, elem):
        if elem == self.identity:
            return '(1)'
        
        cp = set(elem.keys())
        s = ''
        while len(cp) > 0:
            start = min(cp)
            if elem[start] != start:
                s += f'({start}'
                current = start
                while elem[current] != start:
                    s += str(elem[current])
                    current = elem[current]
                    if current in cp:
                        cp.remove(current)
                    else:
                        break
                s += ')'
                if start in cp:
                    cp.remove(start)
            else:
                cp.remove(start)
        return s

def get_all_forms(n, l_max, c_index):
    lower = c_index > 0 # Skip redundant singles

    forms = [("", [])]
    for i in range(lower + 1, min(n, l_max) + 1):
        
        s = '('
        for j in range(i):
            s += chr(c_index + j + ord('a'))
        s += ')'

        suffixes = get_all_forms(n - i, i, c_index + i)

        for suffix in suffixes:
            forms.append((s + suffix[0], [len(s) - len('()')] + suffix[1]))

    return forms

def element_count(lengths, n):
    return int(math.factorial(n) / math.prod([math.factorial(lengths.count(i)) * i ** lengths.count(i) for i in range(1, n + 1)]))
    
def latex_form_table(n):
    print('\\begin{tabular}{|c|c|c|}')
    print('\\hline')
    print('Form & Order & \\# Elements \\\\')
    print('\\hline')
    for form, lengths in get_all_forms(n, n, 0):
        if form != '':
            order = reduce(math.lcm, lengths)
            count = element_count(lengths + [1] * (n - sum(lengths)), n)

            print(f'${form}$ & ${order}$ & ${count}$\\\\')
            print('\\hline')
    print('\\end{tabular}')
