conf_dir=$1
date
echo "  [starting directory preparation $conf_dir]"
python3 gnubg_duel_simulation.py $conf_dir preparator
echo

date
echo "  [setting up player clients]"
x-terminal-emulator -e 'sh -c "python3 gnubg_duel_simulation.py '"$conf_dir"' client_0 | gnubg -t"'
x-terminal-emulator -e 'sh -c "python3 gnubg_duel_simulation.py '"$conf_dir"' client_1 | gnubg -t"'
sleep 1
echo

leg_dirs=(${conf_dir}leg*/)
for leg_dir in "${leg_dirs[@]}"
do
  date
  echo "  [starting simulations $leg_dir]"
  python3 gnubg_duel_simulation.py $leg_dir table | gnubg -t > /dev/null
  echo

  date
  echo "  [starting aggregations $leg_dir]"
  python3 gnubg_duel_simulation.py $leg_dir scorekeeper
  echo
done

date
echo "  [completed $conf_dir]"
echo