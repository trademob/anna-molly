import yaml

# JSON load yeilds strings in Unicode
# use YAML parser instead.


def load(path):
    with open(path) as f:
        config = yaml.load(f.read())
    return config
