import os

dirname = os.path.dirname(__file__)

# Import all the subdirectories
for module in os.listdir(dirname):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
