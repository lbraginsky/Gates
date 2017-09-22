'''
Created on Sep 18, 2017

@author: lbraginsky
'''

def bit(v, k): return (v>>k)&1
def from_bits(bits): return sum(b<<i for i, b in enumerate(bits))
def to_bits(n, v): return [bit(v, i) for i in range(2**n)]
def fmt(n, v): return ''.join(map(str, to_bits(n, v)))
def VAR(n, k): return from_bits(([0]*2**k + [1]*2**k) * 2**(n-k-1))
def VARS(n): return { VAR(n, k): chr(ord('A')+k) for k in range(n) }

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

def min_circuits(n, x, inputs=None):
    """
    Make minimal circuits for all gates
    x is the list of available gates (by name)
    returns a dictionary { gate_number: (size, tree) } where size is the number
    of gates in the circuit and tree is a node: input (string) or tuple
    (gate, node, node)
    """
    inputs = inputs or [VAR(n, k) for k in range(n)]

    def G(g, a, b): return bit(g, a+a+b)
    def combine(g, x, y):
        return reduce(lambda u, v: u|v, (G(g, bit(x, i), bit(y, i)) << i
                                         for i in range(1<<n)))

    x_gates = [gates_by_name[i] for i in x]
    results = { i: (0, i) for i in inputs }

    def count_gates(u, v):
        c = set()
        def add(n):
            w = results[n][1]
            if type(w) is tuple:
                c.add(w)
                _g, a, b = w
                add(a)
                add(b)
        add(u)
        add(v)
        return len(c) + 1
    
    count = 0
    while True:
        change = False
        avail = list(results)
        uv = [(u, v) for u in avail for v in avail]
        count += 1
        for g in x_gates:
            for u, v in uv:
                w = combine(g, u, v)
                if w==u or w==v: continue
                nw = count_gates(u, v)
                if not w in results or nw < results[w][0]:
                    results[w] = (nw, (g, u, v))
                    change = True
        if not change: break
    return results

def circuit_str(vv, results, i):
    def cs(i):
        _size, c = results[i]
        if not (type(c) is tuple): return vv[c]
        g, a, b = c
        return "({} {} {})".format(gates[g], cs(a), cs(b))
    return cs(i)

if __name__ == '__main__':
    
    def min_circuits_test(n, x):
        print "\nAll gates from {} {} inputs".format(x, n)
        print "Inputs"
        vv = VARS(n)
        for v in sorted(vv):
            print "{:10} {}".format(fmt(n, v), vv[v])
        print "Outputs"
        results = min_circuits(n, x)
        for g in range(1<<(1<<n)):
            size, cs = (results[g][0], circuit_str(vv, results, g)) if g in results else ('-', '-')
            print "{:10} [{}] {}".format(fmt(n, g), size, cs)

    n = 3
#     min_circuits_test(n, ["AAndNotB"])
    min_circuits_test(n, ["Nand"])
#     min_circuits_test(n, ["And", "Or", "NotA"])
#     min_circuits_test(n, ["And", "NotA"])

    import cProfile
    import pstats
    
    def profile(cmd):
        profileName = 'profile'
        cProfile.run(cmd, profileName)
        p = pstats.Stats(profileName)
        p.strip_dirs().sort_stats('time').print_stats()
    
#     profile('min_circuits_test(n, ["Nand"])')
