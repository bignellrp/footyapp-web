# footyapp-web

A web app for managing a 5 a side footy team.

Select the players using the checkboxes and it should output a balanced team for each side.

Coded using Python, HTML and Flask using
[grayscale bootstrap template](https://startbootstrap.com/theme/grayscale)

Converted all GET, POST, UPDATE and DELETE commands so Footyapp can use REST.

See REST api here: https://github.com/bignellrp/footyapp-api

To deploy edit the docker-compose for your local IP and network interface and configure the .env

The Discord tokens and webhooks will need to be generated using the following guide:

https://support-dev.discord.com/hc/en-us/articles/360028717192-Where-can-I-find-my-Application-Team-Server-ID-

Configure the username and password in .env

# docker-compose.yml
```
version: '3.8'

services:
  footyapp-web:
    image: ghcr.io/bignellrp/footyapp-web:${BRANCH}
    container_name: footyapp-web-${BRANCH}
    networks:
      br0:
        ipv4_address: ${IPV4_ADDRESS}
    ports:
      - "80:80"
    restart: always
    env_file:
      - /mnt/docker/footyapp-web-${BRANCH}/.env
    environment:
      - TZ=Europe/London

networks:
  br0:
    external: true
    name: br0
```

# .env
```
SESSION={random string}
GIT_BRANCH=main
DISCORD_WEBHOOK=https://discord.com/api/webhooks/{generatewebhook}
DISCORD_WEBHOOK_DEV=https://discord.com/api/webhooks/{generatewebhook}
DISCORD_CLIENT_ID={generatetoken}
DISCORD_CLIENT_SECRET={generatetoken}
DISCORD_CLIENT_ID_DEV={generatetoken}
DISCORD_CLIENT_SECRET_DEV={generatetoken}
DISCORD_REDIRECT_URI=http://127.0.0.1:5000/callback
DISCORD_REDIRECT_URI_DEV=http://127.0.0.1:5000/callback
GAMEDAY=WEDNESDAY
API_TOKEN={apitoken}
API_URL=http://{api_ipv4}
```