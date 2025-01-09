# KeenUtils
Various utilities for managing Keenetic devices

## Currently supported features
* [XKeen](https://github.com/Skrill0/XKeen) configurator ✨
* Static DNS record editor
* System status endpoint

## Deploying with Docker
```bash
docker run --name keen-utils \
  -p 5000:5000 \
  -e KEENETIC_PASSWORD=MY_PASSWORD \
  -e ENTWARE_PASSWORD=MY_ENTWARE_PASSWORD \
  ghcr.io/dmitryarkh/keen-utils:latest
```
### Environment variables
| Name              | Description                                    |
|-------------------|------------------------------------------------|
| HOST              | Keenetic device IP (default: `192.168.1.1`)    |
| SSH_PORT          | Keenetic SSH port (default: `22`)              |
| KEENETIC_USER     | Keenetic web panel username (default: `admin`) |
| KEENETIC_PASSWORD | Keenetic web panel password                    |
| ENTWARE_SSH_PORT  | Entware SSH port (default: `222`)              |
| ENTWARE_USER      | Entware SSH username (default: `root`)         |
| ENTWARE_PASSWORD  | Entware SSH password (default: `keenetic`)     |