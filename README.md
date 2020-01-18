__Holmgång__ is a framework for evaluation of backgammon Match Equity Tables.  
It allows you to run a large amount of matches between two __GNU Backgammon__ bots, each playing according to their own MET.  
With the help of match outcomes and metrics based on those it is possible to reach a verdict about which of the two METs is superior.

## How to run?
First you have to create a directory where the logs of the matches will be saved.  
A `config.yml` file containing the simulations parameters has to be created in your directory. For a valid example see the `example_setups` directory.  
Then you can start running the simulations by issuing the following command from the root directory of __Holmgång__:  
`bash single_leg_framework.sh path/to/your/directory/`  

## How to interpret the output?
In the printout you will see a count of matches won for both players.  
There is a third count for ties. A match is considered drawn if the scores reach either '1 away - 1 away' or '2 away - 2 away' anytime during the match, and does not contribute to the count of wins for any of the players, regardless of the match's actual outcome.  

## Technical requirements, known limitations
__Holmgång__ has only been tested on __Ubuntu 18.04__.  
It needs __Python3__, __Bash__ and __GNU Backgammon__ installed.  
As of January 2020, __GNU Backgammon__ has to be manually compiled, as there is not yet any official release which contains the fixes introduced with the following necessary revisions:  
- `/gnubg/external.c` 1.101  
- `/gnubg/play.c` 1.463  
