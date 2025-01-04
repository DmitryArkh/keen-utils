# KeenUtils
Various web utilities for Keenetic devices 

## Currently supported features
* View static DNS records

## Deploying with Docker
```bash
docker run --name keen-utils \
  -p 5000:5000 \
  -e KEENETIC_PASSWORD=MY_PASSWORD \
  -e ENTWARE_PASSWORD=MY_ENTWARE_PASSWORD \
  ghcr.io/dmitryarkh/keen-utils:main
```
