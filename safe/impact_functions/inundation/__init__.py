import os

dirname = os.path.dirname(__file__)

# Import all the subdirectories
for module in os.listdir(dirname):
    if (module == '__init__.py' or module[-3:] != '.py' or
        module.startswith('.#')) or module.startswith('test_'):
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except ImportError:
        # Most likely not Qt4 / QGIS present
        continue
