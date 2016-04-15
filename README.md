vWeb - SImple Web console for vShield and vCloud Director
=========================================================

Install/Prepare
---------------

Using Virtualenv

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Add vShield(vsm) and vCloud Director(vcd) url to settings.py file.

```
vshield_url = 'https://vcd.com/api'
vcd_url = "https://vshield.com/api"
```
