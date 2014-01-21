---------------------------------
Deployment Notes:
---------------------------------

Setup root user (admin user)
----------------
ssh -i ~/Downloads/blacklisted.pem ubuntu@<public dns>
sudo passwd root (follow steps)
su root
cd /root/.ssh
nano authorized_keys (edit to only contain necessary public keys)
exit
exit

Setup python process user
-------------------
adduser watchl4d


-- INSTALL REQUIREMENTS.SYSTEM
-- INSTALL REQUIREMENTS.PIP

Get Code
--------
cd /var
git clone https://github.com/harterc1/watchl4d.git

Create Database
---------------
# setup postgres user password
sudo -u postgres psql postgres
\password postgres
<type password>
\q

# create db
sudo -u postgres psql
CREATE DATABASE watchl4d;
\q

cd /var/watchl4d
python manage.py syncdb