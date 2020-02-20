import yaml

with open('configs/core/packages.yaml', 'r') as f:
    y = yaml.full_load(f.read())

minimal = []
for v in y['variants']['minimal']['packages']:
    if isinstance(v, str):
        minimal.append(v)

lite = []
for v in y['variants']['lite']['packages']:
    if isinstance(v, str):
        lite.append(v)


packages = []
with open('docs/versions/debootstrap.txt', 'r') as f:
    for line in f.readlines():
        words = line.split()
        if words[0] != 'ii':
            continue

        packages.append(words[1])

print("Common packages between debootstrap and minimal")
print(set(minimal) & set(packages))

packages = []
with open('docs/versions/minimal.txt', 'r') as f:
    for line in f.readlines():
        words = line.split()
        if words[0] != 'ii':
            continue

        packages.append(words[1])

print("Common packages between minimal and lite")
print(set(lite) & set(packages))