# Homelab & Self-Hosted Solutions - 2026

## Overview

Running your own services at home is increasingly popular for privacy, cost savings, learning, and redundancy. Here's a comprehensive guide.

## Why Homelab?

- Privacy (your data stays yours)
- Learn new technologies
- Save on subscription costs
- Full control over your data
- Customization and flexibility

## Common Hardware Options

### Small/Simple
- Raspberry Pi 5 (4-8GB RAM)
- Older laptop or desktop
- Synology/QNAP NAS

### Medium
- Intel NUC or similar
- HP ProDesk/MicroServer
- Custom build (good thermals important)

### Advanced
- Server-grade hardware
- TrueNAS scale-out
- Proxmox cluster

## Essential Services to Self-Host

### Core Infrastructure

**AdGuard Home** - DNS-level ad/tracker blocking
- Blocks ads network-wide
- Easy setup, low resource

**Pi-hole** - Alternative to AdGuard
- Mature, well-documented

**Traefik** - Reverse proxy
- Automatic SSL
- Docker integration
- Let's Encrypt built-in

**Cloudflare Tunnel** - External access without port forwarding

### Media

**Jellyfin** - Media server (free, open-source)
- Emby/Plex alternative
- Hardware transcoding support

**Sonarr/Radarr** - Automated media management
- Downloads, organizes media

**Plex** - Popular media server
- Free for local, subscription for remote

### Productivity

**Nextcloud** - All-in-one productivity
- Files, calendar, contacts, office
- Docker available

**Paperless-ngx** - Document management
- Scan, organize, search documents

**Homarr** / **Homepage** - Dashboard
- Visual overview of services

### Communication

**Matrix (Synapse)** - Open messaging
- E2E encrypted
- Federated (talk to other servers)

**Mealie** - Meal planning
- Recipes, shopping lists

### Automation

**Home Assistant** - Home automation
- Massive integration ecosystem
- Runs well on Pi or NUC

**Node-RED** - Visual automation
- IoT workflows

**Traefik** - Already mentioned, essential

### Security

**Authelia** / **Authentik** - SSO and 2FA
- Single login for all services

**Vaultwarden** - Password manager
- Bitwarden compatible, self-hosted

**Wazuh** - SIEM (if advanced)

## Docker & Container Management

### Recommended Tools
- **Portainer** - Web UI for Docker
- **Dockge** - Lightweight alternative
- **Yacht** - Another Docker UI

### Sample docker-compose.yml
```yaml
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/traefik.yml:ro
    networks:
      - proxy

  jellyfin:
    image: jellyfin/jellyfin
    volumes:
      - ./config:/config
      - ./media:/media
    environment:
      - TZ=America/New_York
    network_mode: host
```

## Networking

### Basic Setup
1. Static IP for server
2. Reserve DHCP addresses
3. Configure router for essential port forwards
4. Consider VLAN segmentation

### Advanced
- WireGuard VPN for remote access
- Cloudflare Tunnel (no port forwarding needed)
- PiVPN for simple VPN
- Tailscale (mesh VPN)

## Backups (Critical!)

### 3-2-1 Rule
- 3 copies of data
- 2 different media types
- 1 offsite (cloud/remote)

### Tools
- **Restic** - Fast, encrypted backups
- **Rclone** - Cloud sync
- **Duplicati** - GUI backup tool
- **Borg Backup** - Deduplicated

### Backup Strategy
```bash
# Simple backup script
#!/bin/bash
restic backup /data \
  --repo s3:https://backups.example.com/homelab \
  --password-file /secrets/passwd
```

## Monitoring

### Tools
- **Grafana + Prometheus** - Metrics and visualization
- **Uptime Kuma** - Uptime monitoring
- **Glances** - System monitoring
- **Dozzle** - Docker logs viewer

### What to Monitor
- CPU/Memory/Disk
- Service health
- Network traffic
- Backup success/failure

## Getting Started Checklist

1. [ ] Choose hardware
2. [ ] Install Proxmox/TrueNAS/Debian
3. [ ] Set up Docker
4. [ ] Configure Traefik
5. [ ] Add AdGuard/Pi-hole
6. [ ] Add authentication (Authelia)
7. [ ] Add desired services
8. [ ] Set up backups
9. [ ] Set up monitoring
10. [ ] Document everything

## Resources

- r/homelab - Community
- LinuxServer.io - Great Docker images
- Awesome Selfhosted - Big service list
- Craftcomputing (YouTube) - Homelab tutorials

## Cost Estimates

| Tier | Hardware | Monthly |
|------|----------|---------|
| Basic (Pi) | $100 | $5-10 (power) |
| Medium (NUC) | $400 | $10-15 |
| Advanced (Server) | $1000+ | $20-40 |

## Legal Considerations

- No commercial use for most self-hosted apps
- Check licenses (some are for personal use only)
- ISP terms of service (residential may block servers)
