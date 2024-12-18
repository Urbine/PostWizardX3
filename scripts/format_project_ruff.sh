curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

ruff format $(pwd/*.py)