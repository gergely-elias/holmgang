__Holmgång__ is a framework for evaluation of backgammon Match Equity Tables.  
It allows you to run a large amount of matches between two __GNU Backgammon__ bots, each playing according to their own MET.  
With the help of match outcomes and metrics based on those it is possible to reach a verdict about which of the two METs is superior.  

## How does it work?
__Holmgång__ runs 3 instances of __GNU Backgammon__: one server which hosts the match (this is basically the table itself), and takes care of generating dice roll sequences, and two clients which connect to the table as external players (using assigned ports on localhost).  
__Holmgång__ communicates with these instances through standard input/output - it basically types commands to set up, start and log matches.  

## How to run?
First you have to create a directory where the logs of the matches will be saved.  
A `config.yml` file containing the simulations parameters has to be created in your directory. For a valid example see the `example_setups` directory.  
Then you can start running the simulations by issuing the following command from the root directory of __Holmgång__:  
`bash framework.sh path/to/your/directory/`  

#### Parameters in the `config.yml` file
- `config_version` (integer) - current value: 1  
- `match_indices` - defines the range of matches to be run: the match index is saved into the match log's filename  
  - `start` (integer) - the match index of the first match to run  
  - `end` (integer) - the match index of the last match to run  
- `superseed` (32-bit integer) - used to generate pseudo-random seeds for individual matches: two matches with identical superseed and match index will use the same dice sequence  
- `rematches` (true/false)  
- `match_length` (positive integer)  
- `met_dir` (string) - path to the directory where XMLs of METs are stored  
- `client_0` & `client_1` - both have the following subfields that describe a player  
  - `name` (string) - the name of the player which will be saved to match logs  
  - `met_file` (string) - XML filename (with extension)  
  - `cube-ply` (integer) - set how many plies to look ahead for cube decisions  
  - `checker-ply` (integer) - sets how many plies to look ahead for checker play  
  - `port` (16-bit integer) - the port which the external player will use to connect to the table  

## How to interpret the output?
In the printout you will see a count of matches won for both players.  
There is a third count for ties. A match is considered drawn if the scores reach either '1 away - 1 away' or '2 away - 2 away' anytime during the match, and does not contribute to the count of wins for any of the players, regardless of the match's actual outcome.  

In case you run rematches, a one-sided t-test will be run to check whether one of the METs is playing significantly stronger than the other.  
The results of matchpairs (which consist of a match and its rematch with the same dice sequence, but roles reversed) are displayed as a cross table. Rows correspond to results of first leg match, columns to results of second leg match. Abbreviations B, W and T stand for Black, White and Tie, respectively.  
Every matchpair provides a score in range of -2 and 2 depending on the results of the two matches in the matchpair. The t-statistics is calculated on the sample of these scores. p-value is then calculated based on that and the degrees of freedom. Finally a verdict is printed that uses 0.05 as a threshold for significance.  

#### Example output of a single leg
(The example below should match the output of the first leg for the example config provided)  
```
     leg score:
     Woolsey 0-ply (White / player 0 / on top): 3
     Zadeh 0-ply (Black / player 1 / bottom): 7
     Ties (scores 1a1a & 2a2a): 0
     Total: 3.0 - 7.0
```

#### Example output of a t-test
(The example below should match the output of the t-test for the example config provided)  
```
     H0: aggregated scores' average is 0
     Matchpair outcomes frequency table:
         B T W
       B 4 2 1
       T 0 0 0
       W 1 0 2
     t-statistics: -0.6123724356957945
     p-value: 0.5554454421055857
     H0 cannot be rejected ~ none of the METs is significantly stronger than the other
```
Note that the sum of rows in the crosstable equal 7, 0 and 3, matching the scores of the first leg in the previous output.  

## Technical requirements, known limitations
__Holmgång__ has only been tested on __Ubuntu 18.04__.  
It needs __Python3__, __Bash__ and __GNU Backgammon__ installed.  
As of March 2020, __GNU Backgammon__ has to be manually compiled, as there is not yet any official release which contains necessary fixes introduced with the following revisions:  
- `/gnubg/external.c` 1.101  
- `/gnubg/play.c` 1.463  
- `/gnubg/external.h` 1.25  
- `/gnubg/drawboard.c` 1.82  
