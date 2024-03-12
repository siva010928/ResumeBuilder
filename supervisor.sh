#!/bin/bash

source env/bin/activate

# Set environment variables here
export DEPLOYMENT_ENVIRONMENT="prod"

cd /var/lib/jenkins/workspace/HHT/

python3 manage.py migrate
echo "Migrations done"
python3 manage.py collectstatic --noinput
echo "collectstatic done"

# giving permission to static files
sudo chmod 770 -R /var/lib/jenkins/workspace/CHECK/staticfiles

cd /var/lib/jenkins/workspace/CHECK

# Delete the old Supervisor configuration file, if it exists
sudo rm -f /etc/supervisor/conf.d/CHECK_SUPERVISOR.conf

# Copy the new Supervisor configuration file
sudo cp CHECK_SUPERVISOR.conf /etc/supervisor/conf.d/CHECK_SUPERVISOR.conf

echo "$USER"
echo "$PWD"

# Reload Supervisor configurations
sudo supervisorctl reread
sudo supervisorctl update

sudo systemctl daemon-reload

# Check the status of the gunicorn process
status=$(sudo supervisorctl -c /etc/supervisor/supervisord.conf status check_gunicorn | awk '{print $2}')

# If gunicorn is running, restart it; otherwise, start it
if [ "$status" = "RUNNING" ]; then
    echo "Gunicorn is running. Restarting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf restart check_gunicorn
else
    echo "Gunicorn is not running. Starting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf start check_gunicorn
fi

# Check the status of the celery_worker process
status=$(sudo supervisorctl -c /etc/supervisor/supervisord.conf status check_celery_worker | awk '{print $2}')

# If celery_worker is running, restart it; otherwise, start it
if [ "$status" = "RUNNING" ]; then
    echo "celery_worker is running. Restarting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf restart check_celery_worker
else
    echo "celery_worker is not running. Starting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf start check_celery_worker
fi

#sudo supervisorctl start gunicorn
#echo "Gunicorn restarted."
#sudo supervisorctl start celery_worker
#echo "Celery Worker restarted."

sudo supervisorctl status check_gunicorn
sudo supervisorctl status check_celery_worker
