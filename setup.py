# General Imports
from setuptools import setup
from Cython.Build import cythonize

# Setup
setup(
    ext_modules = cythonize(["./game/deck.pyx", "./game/game.pyx", "./game/timeAllocator.pyx", \
                             "./player/player.pyx", "./player/grabAndDuckPlayer.pyx", \
                             "./player/mctsPlayer.pyx", "./player/mlPlayer.pyx", \
                             "./player/mlRolloutPlayer.pyx", \
                             "./player/randomGrabAndDuckPlayer.pyx", \
                             "./player/randomPlayer.pyx", "./player/yieldPlayer.pyx", \
                             "./player/rolloutPlayer.pyx"]),
)
