#!/bin/bash
eval `ssh-agent`

ssh-add ~/.ssh/github_ssh_key_1

# Stash any local changes
git stash

# Pull the latest changes from your version control system (e.g., Git)
git pull origin main

# Check if the pull was successful
if [ $? -eq 0 ]; then
    echo "Successfully pulled the latest changes from the repository."
else
    echo "Failed to pull the latest changes. Check your network connection or repository configuration."
    exit 1
fi

cp ../alembic.ini .
cp ../config.py ms_invoicer/

alembic upgrade head

# Check if the migration was successful
if [ $? -eq 0 ]; then
    echo "Database migration completed successfully."
else
    echo "Failed to run database migration. Check your migration scripts and database configuration."
    exit 1
fi

# Restart the necessary services or processes
echo "Restarting services..."
sudo systemctl restart invoicer
sudo systemctl status invoicer

echo "Script execution completed successfully."