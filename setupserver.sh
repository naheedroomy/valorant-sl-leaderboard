!/bin/bash

# Update the package list and install nginx
sudo apt update
sudo apt install -y nginx
sudo apt install -y python3-pip

pip install virtualenv
virtualenv venv
source venv/bin/activate
apt-get install redis-server
systemctl start redis-server
systemctl enable redis-server
pip install -r requirements.txt

# Create the nginx server block configuration
cat <<EOL | sudo tee /etc/nginx/sites-available/valorant.conf
server {
    listen 80;
    server_name www.valorantsl.com valorantsl.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOL

# Create a symbolic link to enable the configuration
sudo ln -s /etc/nginx/sites-available/valorant.conf /etc/nginx/sites-enabled/

# Remove the default server block if it exists
if [ -L /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Test nginx configuration and reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Output to check if nginx reloaded successfully
if [ $? -eq 0 ]; then
    echo "Nginx reloaded successfully!"
else
    echo "Nginx failed to reload. Please check the configuration."
fi
