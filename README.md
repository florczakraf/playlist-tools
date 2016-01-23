# About
Project for Advanced Python course @ ii uwr

Production server: https://yt.rflorczak.eu
# Installation (for Debian based distros)
```
sudo apt-get install python python-pip python-django`
pip install google-api-python-client
pip install django-widget-tweaks
```
### Running in production (wsgi)
First run:
```
sudo apt-get install apache2-dev python-dev
git clone https://github.com/GrahamDumpleton/mod_wsgi
cd mod_wsgi && python setup.py install
```
then go to project directory and:
```
./manage.py collectstatic
mod_wsgi-express start-server playlist_tools/wsgi.py
```
