# General Imports
from setuptools import setup
from Cython.Build import cythonize

# Setup
setup(
    ext_modules = cythonize(["./game/deck.pyx", "./game/game.pyx", "./game/timeAllocator.pyx", \
                             "./player/player.pyx", "./player/grabAndDuckPlayer.pyx"]),
)
