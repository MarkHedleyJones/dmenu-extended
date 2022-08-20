#!/usr/bin/env bash

run_test() {
  # Generate a cache file with required number of entries
  local base_number=10000000000000 # Just to add more digits

  num_entries=$1
  seq ${base_number} $((base_number + num_entries - 1)) >~/.cache/dmenu-extended/dmenuExtended_all.txt
  echo "Running test: Time to load cache of ${num_entries} entries ..."
  { time dmenu_extended_run 1>/dev/null; } 2>/tmp/time.log
  local time_real=$(cat /tmp/time.log | grep real | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
  local time_user=$(cat /tmp/time.log | grep user | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
  local time_sys=$(cat /tmp/time.log | grep sys | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
  local time_real=${time_real::-1} # Cut the 's' from the end of the string
  local time_user=${time_user::-1} # Cut the 's' from the end of the string
  local time_sys=${time_sys::-1}   # Cut the 's' from the end of the string
  local time_diff_real=$(echo "print(round(${time_real} - ${time_empty_real}, 3))" | python3)
  local time_diff_user=$(echo "print(round(${time_user} - ${time_empty_user}, 3))" | python3)
  local time_diff_sys=$(echo "print(round(${time_sys} - ${time_empty_sys}, 3))" | python3)
  echo " - Real time: ${time_real}s (${time_diff_real}s longer than empty cache)"
  echo " - User time: ${time_user}s (${time_diff_user}s longer than empty cache)"
  echo " - System time: ${time_sys}s (${time_diff_sys}s longer than empty cache)"
  echo ""
}

# Generate the required dmenu-extended configuration files etc
dmenu_extended_cache_build >/dev/null
echo "Running test: Time to open menu (empty cache)"
echo "" >~/.cache/dmenu-extended/dmenuExtended_all.txt
{ time dmenu_extended_run 1>/dev/null; } 2>/tmp/time-empty.log
time_empty_real=$(cat /tmp/time-empty.log | grep real | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
time_empty_user=$(cat /tmp/time-empty.log | grep user | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
time_empty_sys=$(cat /tmp/time-empty.log | grep sys | xargs | cut -d ' ' -f 2 | cut -d 'm' -f 2)
time_empty_real=${time_empty_real::-1} # Cut the 's' from the end of the string
time_empty_user=${time_empty_user::-1} # Cut the 's' from the end of the string
time_empty_sys=${time_empty_sys::-1}   # Cut the 's' from the end of the string
echo " - Real time: ${time_empty_real}s"
echo " - User time: ${time_empty_user}s"
echo " - System time: ${time_empty_sys}s"
echo ""

run_test 1000
run_test 20000
run_test 100000
