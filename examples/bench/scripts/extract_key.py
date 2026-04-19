import sys, json

data = json.load(sys.stdin)
key = sys.argv[1]
print(data[key])
