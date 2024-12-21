curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

find . -name "*.py" -not -path "./.venv/*" | xargs ruff format