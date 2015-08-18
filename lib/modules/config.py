import yaml

# JSON load yields strings in Unicode
# use YAML parser instead.


def load(path):
    with open(path) as f:
        config = yaml.load(f.read())
    return config
