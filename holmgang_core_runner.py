import yaml
import sys
import os
import re
import glob
import scipy.stats
import collections
import itertools

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def load_config():
  global work_dir, client_name, config
  if not len(sys.argv) == 3:
    raise Exception('needs two arguments (path and client name)', sys.argv)
  work_dir = sys.argv[1]
  if not work_dir.endswith('/'):
    raise Exception(work_dir, 'does not look like being a directory (it should end with "/")')
  if not os.path.isdir(work_dir):
    raise Exception('no such directory:', work_dir)
  if not os.path.isfile(work_dir + 'config.yml'):
    raise Exception('no config.yml found in', work_dir)
  config = yaml.safe_load(open(work_dir + 'config.yml'))
  client_name = sys.argv[2]
  if client_name not in ['table', 'client_0', 'client_1', 'scorekeeper', 'preparator', 'stat']:
    raise Exception('client name must be one of table/client_0/client_1/scorekeeper/preparator/stat, invalid value:', client_name)

def check_config():
  if not config['config_version'] == 1:
    raise Exception('config.yml version mismatch')

def prepare_legs():
  os.mkdir(work_dir + 'leg1/')
  config_file = open(work_dir + 'leg1/' + 'config.yml', 'w')
  yaml.dump(config, config_file, default_flow_style = False)
  if config['rematches']:
    os.mkdir(work_dir + 'leg2/')
    rematch_config = config.copy()
    rematch_config['client_0'], rematch_config['client_1'] = rematch_config['client_1'], rematch_config['client_0']
    rematch_config_file = open(work_dir + 'leg2/' + 'config.yml', 'w')
    yaml.dump(rematch_config, rematch_config_file, default_flow_style = False)

def start_player(player):
  print('set eval sameasanalysis off')
  print('set met', config['met_dir'] + config[player]['met_file'])
  print('set evaluation chequerplay eval plies', config[player]['checker-ply'])
  print('set evaluation cubedecision eval plies', config[player]['cube-ply'])
  print('external 127.0.0.1:' + str(config[player]['port']))

def start_table():
  for player_id in ['0', '1']:
    print('set player ' + player_id + ' external 127.0.0.1:' + str(config['client_' + player_id]['port']))
  print('set rng mersenne')
  for match_index in range(config['match_indices']['start'], config['match_indices']['end'] + 1):
    seed = match_index
    seed_shuffled = False
    while seed > 4294967295 or not seed_shuffled:
      seed = (pow(2576980389, seed, 4294967311) * 858993463 + config['superseed']) % 4294967310
      seed_shuffled = True
    print('set seed', seed)
    print('new match', config['match_length'])
    for player_id in ['0', '1']:
      print('set player ' + player_id + ' name', config['client_' + player_id]['name'])
    print('save match', work_dir + 'match' + str(match_index) + '.sgf')

def get_match_winner(game_results, match_length):
  match_score_away = {'B': match_length, 'W': match_length}
  for (game_winner, scores_won) in game_results:
    match_score_away[game_winner] -= int(scores_won)
    for tie_away in [2, 1]:
      if (match_score_away['B'] == tie_away and match_score_away['W'] == tie_away):
        return 'T'
    if match_score_away[game_winner] <= 0:
      return game_winner

def collect_and_aggregate_results():
  filenames = glob.glob(work_dir + 'match*.sgf')
  match_length = config['match_length']
  results = {'B': 0, 'W': 0, 'T': 0}

  for filename in filenames:
    match_file = open(filename, 'r')
    lines = ''.join(match_file.readlines())
    pattern = re.compile('RE\[(?P<game_winner>[BW])\+(?P<points_won>\d+)R?\]')
    game_results = pattern.findall(lines)
    match_winner = get_match_winner(game_results, match_length)
    results[match_winner] += 1

  print(bcolors.BLUE, end='')
  print('    ', 'leg score:')
  print('    ', config['client_0']['name'], '(White / player 0 / on top):', results['W'])
  print('    ', config['client_1']['name'], '(Black / player 1 / bottom):', results['B'])
  print('    ', 'Ties (scores 1a1a & 2a2a):', results['T'])
  print('    ', 'Total:', results['W'] + results['T'] / 2, '-', results['B'] + results['T'] / 2)
  print(bcolors.ENDC, end='')

def t_test():
  matchpair_scores = []
  matchpair_score_counts = collections.defaultdict(lambda: 0)
  matchpair_outcome_score = {}
  for match_outcomes in itertools.product('BTW', repeat = 2):
    matchpair_outcome_score[''.join(match_outcomes)] = 'BTW'.index(match_outcomes[0]) - 'BTW'.index(match_outcomes[1])

  for match_index in range(config['match_indices']['start'], config['match_indices']['end'] + 1):
    filenames = [work_dir + 'leg' + leg_id + '/' + 'match' + str(match_index) + '.sgf' for leg_id in ['1', '2']]
    match_length = config['match_length']
    match_results = []

    for filename in filenames:
      match_file = open(filename, 'r')
      lines = ''.join(match_file.readlines())
      pattern = re.compile('RE\[(?P<game_winner>[BW])\+(?P<points_won>\d+)R?\]')
      game_results = pattern.findall(lines)
      match_winner = get_match_winner(game_results, match_length)
      match_results.append(match_winner)

    matchpair_scores.append(matchpair_outcome_score[''.join(match_results)])
    matchpair_score_counts[''.join(match_results)] += 1
  t_statistics, p_value = scipy.stats.ttest_1samp(matchpair_scores, 0)
  print(bcolors.BLUE, end='')
  print('    ', 'H0: aggregated scores\' average is 0')
  print_outcome_frequency_table(matchpair_score_counts)
  print('    ', 't-statistics:', t_statistics)
  print(bcolors.BOLD, end='')
  print('    ', 'p-value:', p_value)
  if p_value < 0.05:
    print(bcolors.RED, end='')
    print('    ', 'H0 must be rejected ~', config['client_' + ('0' if t_statistics > 0 else '1')]['name'], 'is significantly stronger than', config['client_' + ('1' if t_statistics > 0 else '0')]['name'])
  else:
    print(bcolors.GREEN, end='')
    print('    ', 'H0 cannot be rejected ~ none of the METs is significantly stronger than the other')
  print(bcolors.ENDC, end='')

def print_outcome_frequency_table(matchpair_score_counts):
  column_width = len(str(max(matchpair_score_counts.values()))) + 1
  print('    ', 'Matchpair outcomes frequency table:')
  print('      ', ' ', end='')
  for match2_outcome in 'BTW':
    print_length(match2_outcome, column_width)
  print()
  for match1_outcome in 'BTW':
    print('      ', match1_outcome, end='')
    for match2_outcome in 'BTW':
      print_length(matchpair_score_counts[match1_outcome + match2_outcome], column_width)
    print()

def print_length(number, length):
  converted_number = str(number)
  print(' ' * (length - len(converted_number)) + converted_number, end='')

load_config()
check_config()
if (client_name == 'scorekeeper'):
  collect_and_aggregate_results()
elif (client_name == 'table'):
  start_table()
elif (client_name == 'preparator'):
  prepare_legs()
elif (client_name == 'stat'):
  t_test()
else:
  start_player(client_name)
