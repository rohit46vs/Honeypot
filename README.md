# Honeypot - Attacker Trap

A beginner-friendly cybersecurity project that sets up fake servers to detect, trap, and log attackers — just like real honeypots used by banks and security teams!

---

## Project Structure

```

├── honeypot.py            # main file
└── README_honeypot.md     # This file
```

---

## Requirements

- Python 3.x
- No extra libraries needed!
- Run VS Code as Administrator (for ports below 1024)

---

## How to Run

```bash
py honeypot.py
```

---

## Features

| Option | What it does |
|---|---|
| 1. Fake SSH Server | Traps attackers trying to brute-force SSH logins |
| 2. Fake HTTP Server | Lures attackers scanning for admin panels |
| 3. Fake FTP Server | Catches FTP login attempts |
| 4. View Log | Shows all recorded attack attempts |
| 5. Clear Log | Resets the attack log |
| 6. Learn Mode | Explains how honeypots work |

---

## Recommended Ports

| Service | Recommended Port | Why |
|---|---|---|
| SSH | 2222 | Real SSH uses 22 (needs admin), 2222 works without |
| HTTP | 8080 | Real HTTP uses 80 (needs admin), 8080 works without |
| FTP | 2121 | Real FTP uses 21 (needs admin), 2121 works without |

---

## How to Test It

### Test your own honeypot:

1. Start the fake SSH honeypot on port 2222
2. Open a NEW terminal window
3. Run this command to connect to your own honeypot:
```bash
ssh -p 2222 localhost
```
4. Type any username and password
5. Switch back to the honeypot terminal — you will see the attack logged!

### Test the HTTP honeypot:
1. Start the fake HTTP server on port 8080
2. Open your browser
3. Go to: http://localhost:8080/admin
4. Watch the honeypot log the suspicious request!

---

## Example Log Output

```
[2024-03-06 14:32:01] [SSH]  192.168.1.10:54321 | Connection established
[2024-03-06 14:32:02] [SSH]  192.168.1.10:54321 | Username attempt: 'root'
[2024-03-06 14:32:03] [SSH]  192.168.1.10:54321 | Password attempt: 'admin123'
[2024-03-06 14:32:04] [SSH]  192.168.1.10:54321 | Access denied - attacker disconnected

[2024-03-06 14:35:10] [HTTP] 192.168.1.15:60234 | Connection established
[2024-03-06 14:35:10] [HTTP] 192.168.1.15:60234 | Request: GET /admin HTTP/1.1
[2024-03-06 14:35:10] [HTTP] 192.168.1.15:60234 | SUSPICIOUS PATH detected: /admin
```

---

## What You Learn From This Project

- What honeypots are and how real companies use them
- How attackers behave when they think they found a target
- Socket programming — creating servers from scratch in Python
- Multi-threading — handling multiple attackers simultaneously
- How SSH, HTTP, and FTP protocols work at a low level
- Log analysis — reading and understanding attack patterns
- The difference between low and high interaction honeypots

---

## How Real Honeypots Are Used

| Industry | How they use honeypots |
|---|---|
| Banks | Detect hackers before they reach real systems |
| Governments | Track and identify cybercriminals |
| Security researchers | Collect malware samples safely |
| Companies | Buy time to respond to attacks |

---

## Legal Warning

Only run this honeypot on YOUR OWN network. Attracting attackers to a network you do not own or administer is illegal. This is for learning on your personal machine only.

---

