"Makefile for Sphinx documentation, adapted to python"
import os
from cloud_sptheme.make_helper import SphinxMaker
if __name__ == "__main__":
    build = os.path.join(os.pardir, "build", "sphinx")
    SphinxMaker.execute(BUILD=build)
