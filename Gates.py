'''
Created on Sep 18, 2017

@author: lbraginsky

Build minimal curcuits out of available gates.
'''
from collections import namedtuple
from _collections import defaultdict

def bit(v, k): return (v>>k)&1

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

Size = namedtuple("Size", ["count", "depth"])
Gate = namedtuple("Gate", ["gate_type", "node_a", "node_b"])
Node = namedtuple("Node", ["size", "value", "gate"])
WorkCircuit = namedtuple("WorkCircuit", ["size", "node"])

# External view
CircuitGate = namedtuple("CircuitGate", ["gate_type", "index", "a", "b"])
Circuit = namedtuple("Circuit", ["size", "gate"])

def min_circuits(x, inputs=["A", "B"]):
    """
    Make minimal circuits for all gates from available gates and terminals
    x is the list of available gates (by name), inputs are terminals
    Returns a dictionary { gate_value: circuits }
    circuits: dictionary { gate_value: (size, gate) }
    size: (count, depth) of the circuit
    gate: (gate_type, index, a, b)
    gate_type: one of the x gates
    index: instance number of the gate (per gate type)
    a, b: gate input values
    """
    def G(g, a, b): return bit(g, a+a+b)
    def combine(g, x, y):
        return reduce(lambda u, v: u|v, (G(g, bit(x, i), bit(y, i)) << i
                                         for i in range(4)))

    x_gates = [gates_by_name[i] for i in x]

    nodes = [Node(size=Size(0, 0), value=g, gate=None)
             for g in (gates_by_name[i] for i in inputs)]
    circuits = {n.value: WorkCircuit(n.size, node=i)
               for i, n in enumerate(nodes)}

    def new_node(g, u, v, depth):
        def count_gates(u, v):
            """ Comupute the number of gates in a circuit with child nodes u, v """
            c = set()
            def add(node_id):
                n = nodes[node_id]
                if n.gate == None: return
                c.add(node_id)
                add(n.gate.node_a)
                add(n.gate.node_b)
            add(u)
            add(v)
            return len(c) + 1
        return Node(size=Size(count=count_gates(u, v), depth=depth),
                    value=combine(g, nodes[u].value, nodes[v].value),
                    gate=Gate(g, u, v))

    depth = 0
    cutoff = 300
    try:
        while True:
            depth += 1
            change = False
            avail = range(len(nodes))
            uv = [(u, v) for u in avail for v in avail]
            for g in x_gates:
                for u, v in uv:
                    node = new_node(g, u, v, depth)
                    if not node.value in circuits or node.size <= circuits[node.value].size:
                        change = True
                        node_id = len(nodes)
                        nodes.append(node)
                        circuits[node.value] = WorkCircuit(size=node.size, node=node_id)
                        if len(nodes) >= cutoff: raise
            if not change: break
    except:
        pass
    
    def circuit(node_id):
        my_circuits = {}
        gates = defaultdict(set)        
        def add(node_id):
            node = nodes[node_id]
            if node.gate is None:
                my_circuits[node.value] = Circuit(node.size, None)
            else:
                g = node.gate
                gate = CircuitGate(g.gate_type, node_id,
                                   nodes[g.node_a].value,
                                   nodes[g.node_b].value)
                my_circuits[node.value] = Circuit(node.size, gate)
                add(g.node_a)
                add(g.node_b)
                gates[g.gate_type].add(node_id)
        add(node_id)
        gate_trans = {(g, v): i+1 for g in gates for i, v in enumerate(gates[g])}
        def trans(g):
            return g and CircuitGate(g.gate_type, gate_trans[g.gate_type, g.index], g.a, g.b)
        return {w: Circuit(c.size, trans(c.gate)) for w, c in my_circuits.iteritems()}

    return {w: circuit(circuits[w].node) for w in circuits}

if __name__ == '__main__':
    
    def min_circuits_test(x, inputs=["A", "B"]):
        print "\nAll gates from {} {}".format(x, inputs)

        results = min_circuits(x, inputs=inputs)

        def fmt_circuit(circuits, w):
            def fmt(w):
                gate = circuits[w].gate
                if not gate: return gates[w]
                return "({}.{} {} {})".format(gates[gate.gate_type], gate.index,
                                              fmt(gate.a), fmt(gate.b))
            return fmt(w)

        for g, g_name in sorted(gates.iteritems()):
            if g in results:
                circuits = results[g]
                count = circuits[g].size.count
                cs = fmt_circuit(circuits, g)
            else:
                count = cs = '-'
            print "{:10} [{}] {}".format(g_name, count, cs)

    min_circuits_test(["Nand"])
    min_circuits_test(["Nor"])
    min_circuits_test(["And", "Or", "NotA"])
    min_circuits_test(["And", "Or"])
    min_circuits_test(["And", "NotA"])
    min_circuits_test(["Or", "NotA"])
    min_circuits_test(["NotAAndB"])
    min_circuits_test(["NotAAndB", "NotA"])
    min_circuits_test(["NotAAndB", "NotAOrB"])
