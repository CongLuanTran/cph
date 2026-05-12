import sys

inp = sys.stdin.buffer.read().split()
it = iter(inp)
ni = lambda: int(next(it))
na = lambda n: [ni() for _ in range(n)]
ns = lambda: next(it).decode()
out = []
write = lambda x: out.append(str(x))

t = ni()

sys.stdout.write("\n".join(out) + "\n")
