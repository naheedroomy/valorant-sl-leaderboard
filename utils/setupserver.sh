#!/bin/bash

sudo apt update
sudo apt install nginx -y
sudo apt install redis -y
sudo bash -c 'cat > /etc/nginx/sites-available/valorantsl.com.conf << EOL
server {
    listen 80;
    server_name valorantsl.com;
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL'

sudo ln -s /etc/nginx/sites-available/valorantsl.com.conf /etc/nginx/sites-enabled/valorantsl.com.conf

sudo apt install certbot python3-certbot-nginx -y

sudo certbot --nginx --agree-tos --redirect --hsts --staple-ocsp --email nroomy1@gmail.com -d valorantsl.com

sudo systemctl restart nginx
