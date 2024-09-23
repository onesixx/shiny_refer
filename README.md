# shiny_refer

conda config --add channels conda-forge
conda env update --file environment.yml

conda install --force-reinstall sqlite


# Code static analysis
check your code first before deploying
```shell
python -m pylint   app.py
python -m pyflakes app.py
python -m mccabe --min=3 app.py
```