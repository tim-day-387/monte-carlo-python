# monte-carlo-python

![Python](https://github.com/tim-day-387/monte-carlo-python/actions/workflows/python-app.yml/badge.svg)
![Reporting](https://github.com/tim-day-387/monte-carlo-python/actions/workflows/make-report.yml/badge.svg)

This code implements card-playing AI using modern AI/machine learning techniques. This was the solo final project for a graduate AI course. The basic implementation (built earlier in the course) for the card game player is in the rollouts-python repository.

The card game that the AI players play, is a monster-themed variation on the game [Hearts](https://en.wikipedia.org/wiki/Hearts_(card_game)#Preliminaries_2) 
aptly called Monster.

# Using the Code

Download or clone the repository and install the packages listed in the 'requirements.txt' file. The Cython modules must be built using the command:\
\
```python3 setup.py build_ext --inplace```\
\
Then, the code can be run using the following command:\
\
```python3 main.py```

# Players 

This repository contains code for eight different card-playing AI. The baseline player, and perhaps the simpliest, is Grab And Duck. This is a simple greedy 
algorithm. It grabs points when it can, and avoids (or ducks) losses when it can. Another AI performs rollouts to make decisions, as often seen in 
[backgammon opening strategy](https://en.wikipedia.org/wiki/Rollout_(backgammon)). Two AI players use a random-forests model trained on data generated 
from simulating games of Monster; the first uses the model alone, while the second pairs it with rollouts.  

# Performance Improvements

The implementation of Monster includes a number of improvements to boost performance, 
extensibility, and readability. The game playing code and the AI
players have been implement using Cython; this package compiles Python
in C for a faster execution time on oft-reused code. One-thousand games of
Monster were played using only Grab and Duck players for a time of:\
\
```28401642 function calls (28388259 primitive calls) in 9.706 seconds```\
\
When the game playing code was setup to use Cython, the time was reduced to:\
\
```13198263 function calls (13184875 primitive calls) in 6.094 seconds```\
\
When the AI players were also setup to use Cython, the time was further
reduced to:\
\
```3168924 function calls (3155536 primitive calls) in 3.523 seconds```\
\
These times were collected using the cProfile utility included in Python.
Multiprocessing was also implemented, which provided a vast decrease in
the amount of time needed to run code. cProfile is more difficult to use for
multiple processes, so the following run has been recorded:
```
timothy@debian-desktop:~/Downloads/monte-carlo-python$ python3 main.py
(33.311600000000006, 736.158917532)
```
This images shows the results of 1,000,000 games of Monster, again with
only Grab And Duck players. The win rate is, understandably, about 1/3.
The execution time was about 12.5 minutes. Both Cython and multiprocessing 
allow for a small amount of compute resources (the computer used is
seven or so years old) to go very far.
