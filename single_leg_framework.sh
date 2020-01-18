conf_dir=$1
echo "starting simulations $conf_dir"
date
echo

x-terminal-emulator -e 'sh -c "python3 gnubg_duel_simulation.py '"$conf_dir"' client_0 | gnubg -t"'
x-terminal-emulator -e 'sh -c "python3 gnubg_duel_simulation.py '"$conf_dir"' client_1 | gnubg -t"'
sleep 1
python3 gnubg_duel_simulation.py $conf_dir table | gnubg -t > /dev/null

echo "starting aggregations $conf_dir"
date
echo
python3 gnubg_duel_simulation.py $conf_dir scorekeeper

echo "completed $conf_dir"
date
echo
