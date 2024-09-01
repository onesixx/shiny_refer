# install rose
rose is a Python package that does something really useful.

- Installation
You can install rose using pip:
```shell
pip install -e .
pip install -e . --use-pep517
```

# Code static analysis
check your code first before deploying
```shell
python -m pylint   app.py
python -m pyflakes app.py
python -m mccabe --min=3 app.py
```

# miscellaneous
shiny express is not covered.