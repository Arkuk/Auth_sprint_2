while ! nc -z $AUTH_POSTGRES_HOST $AUTH_POSTGRES_PORT; do
  sleep 5
done
cd src
flask db upgrade
flask create-roles
flask createsuperuser $AUTH_ADMIN_NAME $AUTH_ADMIN_PASSWORD
gunicorn wsgi_app:app -b 0.0.0.0:8000 -w 3
