import yaml
import sys
import os
import re
import glob

def load_config():
  global work_dir, client_name, config
  work_dir = sys.argv[1]
  if not work_dir.endswith('/'):
    raise Exception(work_dir, 'does not look like being a directory (it should end with "/")')
  if not os.path.isdir(work_dir):
    raise Exception('no such directory:', work_dir)
  if not os.path.isfile(work_dir + 'config.yml'):
    raise Exception('no config.yml found in', work_dir)
  config = yaml.safe_load(open(work_dir + 'config.yml'))
  client_name = sys.argv[2]
  if client_name not in ['table', 'client_0', 'client_1', 'scorekeeper', 'preparator']:
    raise Exception('client name must be one of table/client_0/client_1/scorekeeper/preparator, invalid value:', client_name)

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
    if ((match_score_away['B'] == 1 and match_score_away['W'] == 1) or (match_score_away['B'] == 2 and match_score_away['W'] == 2)):
      return 'T'
    elif match_score_away[game_winner] <= 0:
      return game_winner

def collect_and_aggregate_results():
  filenames = glob.glob(work_dir + 'match*.sgf')
  match_length = config['match_length']
  results = {'B': 0, 'W': 0, 'T': 0}

  for filename in filenames:
    match_id = re.findall('\d+', filename)[-1]
    match_file = open(filename, 'r')
    lines = ''.join(match_file.readlines())
    pattern = re.compile('RE\[(?P<game_winner>[BW])\+(?P<points_won>\d+)R?\]')
    game_results = pattern.findall(lines)
    match_winner = get_match_winner(game_results, match_length)
    results[match_winner] += 1

  print('    ', 'leg score:')
  print('    ', config['client_0']['name'], '(White / player 0 / on top):', results['W'])
  print('    ', config['client_1']['name'], '(Black / player 1 / bottom):', results['B'])
  print('    ', 'Ties (scores 1a1a & 2a2a):', results['T'])
  print('    ', 'Total:', results['W'] + results['T'] / 2, '-', results['B'] + results['T'] / 2)

load_config()
check_config()
if (client_name == 'scorekeeper'):
  collect_and_aggregate_results()
elif (client_name == 'table'):
  start_table()
elif (client_name == 'preparator'):
  prepare_legs()
else:
  start_player(client_name)
