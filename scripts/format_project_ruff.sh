curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
elif [ "$venv" = 1 ];then

   cd ..
fi

venv=$(pwd | grep -c venv)
if [ "$venv" = 1 ];then
  # Go to parent dir if executed from .venv
  cd ..
else
  :
fi

find . -name "*.py" -not -path "./.venv/*" | xargs ruff format