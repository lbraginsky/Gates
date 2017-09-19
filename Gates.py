'''
Created on Sep 18, 2017

@author: lbraginsky
'''

gates = {
         0b0000: "False",
         0b0001: "Nor",
         0b0010: "NotAAndB",
         0b0011: "NotA",
         0b0100: "AAndNotB",
         0b0101: "NotB",
         0b0110: "Xor",
         0b0111: "Nand",
         0b1000: "And",
         0b1001: "Xnor",
         0b1010: "B",
         0b1011: "NotAOrB",
         0b1100: "A",
         0b1101: "AOrNotB",
         0b1110: "Or",
         0b1111: "True",
         }

gates_by_name = { name: value for value, name in gates.iteritems() }

def min_circuits(x, inputs=["A", "B"]):
    """
    Make minimal circuits for all gates
    x is the list of available gates (by name)
    returns a dictionary { gate_number: (size, tree) } where size is the number
    of gates in the circuit and tree is a node: input (string) or tuple
    (gate, node, node)
    """
    def G(g, a, b):
        return (g >> (a+a+b)) & 1

    def combine(g, x, y):
        return reduce(lambda u, v: u|v,
                      (G(g, G(x, a, b), G(y, a, b)) << (a+a+b)
                       for a in (0, 1) for b in (0, 1)))

    x_gates = [(gates_by_name[i], i) for i in x]
    results = { gates_by_name[i]: (0, i) for i in inputs }
    while True:
        change = False
        avail = list(results)
        for g, g_name in x_gates:
            uv = ((u, v) for u in avail for v in avail)
            for u, v in uv:
                nu, cu = results[u]                
                nv, cv = results[v]
                w = combine(g, u, v)
                nw = nu + nv + 1
                if not w in results or nw < results[w][0]:
                    results[w] = (nw, (g_name, cu, cv))
                    change = True
        if not change: return results

if __name__ == '__main__':
    
    def circuit_str(c):
        if type(c) is str: return c
        g, a, b = c
        return "({} {} {})".format(g, circuit_str(a), circuit_str(b))

    def min_circuits_test(x, inputs=["A", "B"]):
        print "\nAll gates from {} {}".format(x, inputs)
        results = min_circuits(x, inputs=inputs)
        for g, g_name in sorted(gates.iteritems()):
            size, circuit = results[g] if g in results else ('-', '-')
            print "{:10} [{}] {}".format(g_name, size, circuit_str(circuit))

    min_circuits_test(["Nand"])
    min_circuits_test(["Nand"], inputs=["A", "B", "True", "False"])
    min_circuits_test(["Nor"])
    min_circuits_test(["And", "Or", "NotA"])
    min_circuits_test(["And", "Or"])
    min_circuits_test(["And", "Or"], inputs=["A", "B", "True", "False"])
    min_circuits_test(["And", "NotA"])
    min_circuits_test(["Xor", "Xnor"])
