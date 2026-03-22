# System Administration & DevOps - Research Notes
## 2026-03-14

---

## 1. Automation Tools

### Configuration Management
| Tool | Description |
|------|-------------|
| Ansible | Agentless, YAML-based |
| Puppet | Declarative, master/agent |
| Chef | Ruby-based, cookbooks |
| Salt | Fast, remote execution |

### Container Orchestration
- **Docker** - Container platform
- **Kubernetes** - Container orchestration
- **Docker Compose** - Multi-container apps
- **Podman** - Daemonless containers

### CI/CD
- **Jenkins** - Open source CI/CD
- **GitHub Actions** - GitHub's CI/CD
- **GitLab CI** - Integrated CI/CD
- **Travis CI** - Cloud CI

---

## 2. Monitoring

### System Monitoring
```bash
# htop - Interactive process viewer
htop

# top - Process monitor
top

# atop - Advanced system monitor
atop

# nmon - IBM performance monitor
nmon

# dstat - Versatile resource statistics
dstat -a
```

### Network Monitoring
- **Nagios** - Infrastructure monitoring
- **Zabbix** - Enterprise monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

### Log Management
- **ELK Stack** - Elasticsearch, Logstash, Kibana
- **Splunk** - Log analysis
- **Graylog** - Centralized logging

---

## 3. Server Administration

### Web Servers
- **Nginx** - High-performance web server
- **Apache** - Mature web server
- **Caddy** - Automatic HTTPS
- **LiteSpeed** - Performance server

### Reverse Proxies
- **Traefik** - Modern reverse proxy
- **HAProxy** - Load balancer
- **Envoy** - Service proxy

### Database Servers
- **PostgreSQL** - Advanced RDBMS
- **MySQL/MariaDB** - Popular RDBMS
- **Redis** - In-memory cache
- **MongoDB** - NoSQL database

---

## 4. Security Hardening

### SSH Hardening
```bash
# Disable password authentication
PasswordAuthentication no

# Use key-based auth only
PubkeyAuthentication yes

# Disable root login
PermitRootLogin no

# Change default port
Port 2222
```

### Firewall
```bash
# UFW (Ubuntu)
ufw enable
ufw allow ssh
ufw allow 80/tcp
ufw deny 23

# iptables
iptables -A INPUT -p tcp --dport 22 -j DROP
iptables -A INPUT -p tcp -s 10.0.0.0/8 --dport 22 -j ACCEPT
```

### Fail2Ban
```bash
# Install
apt install fail2ban

# Configure
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

---

## 5. Backup Solutions

### Tools
- **rsync** - File synchronization
- **Rclone** - Cloud sync
- **Borg** - Deduplicating backup
- **Duplicati** - Encrypted backup
- **Amanda** - Enterprise backup

### Example rsync
```bash
# Local backup
rsync -avz /source /destination

# Remote backup
rsync -avz -e ssh /source user@server:/backup

# With exclusion
rsync -avz --exclude='*.log' /source/ /destination/
```

---

## 6. Virtualization

### Tools
- **QEMU/KVM** - Full virtualization
- **VirtualBox** - Desktop virtualization
- **Proxmox** - Server virtualization
- **VMware** - Commercial virtualization

---

## 7. Cloud Platforms

### Common Services
- **AWS** - Amazon Web Services
- **Azure** - Microsoft cloud
- **GCP** - Google Cloud Platform
- **DigitalOcean** - Simple cloud

### CLI Tools
```bash
# AWS
aws s3 cp file.txt s3://bucket/

# Azure
az vm list

# GCP
gcloud compute instances list
```

---

## 8. Useful Commands

### Process Management
```bash
# Find process
ps aux | grep nginx

# Kill process
kill -9 PID

# List open files
lsof -i :80

# Check ports
netstat -tulpn
```

### Disk Usage
```bash
# Disk space
df -h

# Directory size
du -sh /var

# Largest files
find / -type f -size +100M
```

### Memory
```bash
# Free memory
free -h

# Memory details
cat /proc/meminfo

# VM stats
vmstat 1
```

---

## 9. Scripting for SysAdmin

### Python for SysAdmin
```python
import subprocess
import psutil
import paramiko

# Run shell command
result = subprocess.run(['df', '-h'], capture_output=True)

# Check process
for proc in psutil.process_iter(['pid', 'name']):
    print(proc.info)

# SSH connection
client = paramiko.SSHClient()
client.connect(hostname, username, password)
```

### Bash Scripts
```bash
#!/bin/bash
# Backup script
DATE=$(date +%Y%m%d)
tar -czf /backup/$DATE.tar.gz /var/www
find /backup -type f -mtime +30 -delete
```

---

## 10. Self-Hosted Applications

### Common Self-Hosted Apps
| Category | Apps |
|----------|------|
| File Storage | Nextcloud, Seafile |
| Passwords | Bitwarden, Vaultwarden |
| Notes | Logseq, Outline |
| Media | Jellyfin, Plex |
| Bookmarks | Shiori, LinkAce |

### Docker Compose Example
```yaml
version: '3'
services:
  nextcloud:
    image: nextcloud
    ports:
      - "8080:80"
    volumes:
      - nextcloud:/var/www/html
    volumes:
  postgres:
    image: postgres
    environment:
      POSTGRES_PASSWORD: secret
```

---

## 11. Learning Resources

### Books
- "The Linux Command Line" - William Shotts
- "UNIX and Linux System Administration Handbook"
- "Infrastructure as Code" - Kief Morris

### Practice Platforms
- **HackTheBox** - Pentesting labs
- **TryHackMe** - Beginner labs
- **OverTheWire** - Wargames

---

*Last Updated: 2026-03-14*
