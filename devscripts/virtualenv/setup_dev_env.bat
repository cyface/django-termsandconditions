REM You must have virtualenv installed, and the virualenv command in your path for this to work.
REM Assuming you have python installed, you can install virtualenv using the command below.
REM curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
REM This should be run from the project directory, not inside the socialprofile dir

virtualenv --system-site-packages django-socialprofile-env
call django-socialprofile-env\Scripts\activate.bat
pip install -r socialprofile_demo/requirements_dev.txt