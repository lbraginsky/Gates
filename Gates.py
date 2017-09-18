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

def min_circuit(x, y):
    """
    x is the list of available gates (by name)
    y is the gate to build (by name)
    returns a tree with nodes (size, gate, operand1, operand2) where size is the
    number of gates in a circuit, and each operand is A, B, or another node
    """
    def gate_out(g, a, b):
        return (g >> (a+a+b)) & 1

    def combine(g, x, y):
        outs = [gate_out(g, gate_out(x, a, b), gate_out(y, a, b))
                for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)]]
        return reduce(lambda a, b: a|b, (out << i for i, out in enumerate(outs)))

    results = { gates_by_name[c]: (0, c) for c in ["A", "B"] }
    x_values = [gates_by_name[g] for g in x]
    y_value = gates_by_name[y]
    while True:
        change = False
        avail = results.keys()
        for g in x_values:
            for u in avail:
                nu = results[u][0]
                for v in avail:
                    nv = results[v][0]
                    w = combine(g, u, v)
                    nw = nu + nv + 1
                    if not w in results or nw < results[w][0]:
                        results[w] = (nw, gates[g], results[u], results[v])
                        change = True
        if not change:
            break
    return results[y_value] if y_value in results else None

if __name__ == '__main__':
    
    def circuit_str(c):
        if c == None: return "Impossible"
        if c[0] == 0: return c[1]
        return "({} {} {})".format(c[1], circuit_str(c[2]), circuit_str(c[3]))

    def all_gates_test(x):
        print
        print "All gates from {}".format(x)
        all_gates = [g for v, g in sorted(gates.iteritems())]
        for g in all_gates:
            circuit = min_circuit(x, g)
            print "{:10} [{}] {}".format(g, (circuit or '-')[0], circuit_str(circuit))

    all_gates_test(["Nand"])
    all_gates_test(["Nor"])
    all_gates_test(["And", "Or", "NotA"])
    all_gates_test(["And", "Or"])
    all_gates_test(["And", "NotA"])
    all_gates_test(["Xor", "Xnor"])
