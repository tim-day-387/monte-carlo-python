# General Imports
from setuptools import setup
from Cython.Build import cythonize

# Setup
setup(
    ext_modules = cythonize(["./game/deck.pyx", "./game/game.pyx"]),
)
