conf_dir=$1
date
echo "  [starting directory preparation $conf_dir]"
python3 holmgang_core_runner.py $conf_dir preparator
echo

date
echo "  [setting up player clients]"
x-terminal-emulator -e 'sh -c "python3 holmgang_core_runner.py '"$conf_dir"' client_0 | gnubg -t"'
x-terminal-emulator -e 'sh -c "python3 holmgang_core_runner.py '"$conf_dir"' client_1 | gnubg -t"'
sleep 1
echo

leg_dirs=(${conf_dir}leg*/)
for leg_dir in "${leg_dirs[@]}"
do
  date
  echo "  [starting simulation $leg_dir]"
  python3 holmgang_core_runner.py $leg_dir table | gnubg -t > /dev/null
  echo

  date
  echo "  [starting match aggregation $leg_dir]"
  python3 holmgang_core_runner.py $leg_dir scorekeeper
  echo
done

if [ ${#leg_dirs[@]} = 2 ]
then
  date
  echo "  [starting t-test calculation $conf_dir]"
  python3 holmgang_core_runner.py $conf_dir stat
  echo
fi

date
echo "  [completed $conf_dir]"
echo
