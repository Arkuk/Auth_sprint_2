while ! nc -z $AUTH_POSTGRES_HOST $AUTH_POSTGRES_PORT; do
  sleep 5
done
cd src
#flask db init
#flask db migrate
flask db upgrade
flask create-roles
flask createsuperuser $AUTH_ADMIN_NAME $AUTH_ADMIN_PASSWORD
python3 pywsgi.py
