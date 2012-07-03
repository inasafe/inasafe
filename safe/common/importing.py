import os
import imp

def import_all(name, path):
    modules = []
    for module in os.listdir(path):
        if module =='__init__.py' or module[-3:] != '.py':
           continue
        absolute_path = "%s.%s" % (name, module[:-3])
        __import__(absolute_path, locals(), globals())
        modules.append(m)
    return modules
