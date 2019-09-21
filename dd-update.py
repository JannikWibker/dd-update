import yaml

f = open("dd-update.yml", "r")

print(yaml.load(f, Loader=yaml.Loader))
