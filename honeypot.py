# ============================================
#   HONEYPOT
#   Project 6 - Cybersecurity Learning Series
# ============================================

import socket
import threading
import datetime
import os
import time

# ── Global attack log ─────────────────────────────────────
attack_log = []
LOG_FILE = "honeypot_log.txt"
running = False


def display_banner():
    print("\n" + "="*55)
    print("   HONEYPOT - ATTACKER TRAP")
    print("="*55)
    print("   Project 6 - Cybersecurity Learning Series")
    print("="*55)


def display_menu():
    print("\n  What would you like to do?")
    print("  [1] Start Honeypot (fake SSH server)")
    print("  [2] Start Honeypot (fake HTTP server)")
    print("  [3] Start Honeypot (fake FTP server)")
    print("  [4] View attack log")
    print("  [5] Clear log")
    print("  [6] Learn how Honeypots work")
    print("  [7] Exit")


def log_event(service, attacker_ip, attacker_port, message):
    """Log an attack attempt."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "time": timestamp,
        "service": service,
        "ip": attacker_ip,
        "port": attacker_port,
        "message": message
    }
    attack_log.append(entry)

    line = f"[{timestamp}] [{service}] {attacker_ip}:{attacker_port} | {message}"
    print(f"\n  *** ATTACKER DETECTED! ***")
    print(f"  {line}")

    # Save to file
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

    return line


def handle_ssh_client(conn, addr, service="SSH"):
    """Handle a fake SSH connection."""
    attacker_ip = addr[0]
    attacker_port = addr[1]

    log_event(service, attacker_ip, attacker_port, "Connection established")

    try:
        # Send fake SSH banner
        conn.send(b"SSH-2.0-OpenSSH_7.4\r\n")
        time.sleep(0.5)

        # Ask for username
        conn.send(b"login as: ")
        username = conn.recv(1024).decode("utf-8", errors="ignore").strip()

        if username:
            log_event(service, attacker_ip, attacker_port, f"Username attempt: '{username}'")

        # Ask for password
        conn.send(b"\r\nPassword: ")
        password = conn.recv(1024).decode("utf-8", errors="ignore").strip()

        if password:
            log_event(service, attacker_ip, attacker_port, f"Password attempt: '{password}'")

        # Always deny access
        time.sleep(1)
        conn.send(b"\r\nAccess denied.\r\n")
        log_event(service, attacker_ip, attacker_port, "Access denied - attacker disconnected")

    except Exception as e:
        pass
    finally:
        conn.close()


def handle_http_client(conn, addr):
    """Handle a fake HTTP connection."""
    attacker_ip = addr[0]
    attacker_port = addr[1]

    log_event("HTTP", attacker_ip, attacker_port, "Connection established")

    try:
        # Receive the HTTP request
        request = conn.recv(4096).decode("utf-8", errors="ignore")

        if request:
            # Extract the request line
            first_line = request.split("\n")[0].strip()
            log_event("HTTP", attacker_ip, attacker_port, f"Request: {first_line}")

            # Check for suspicious paths
            suspicious = ["/admin", "/wp-admin", "/.env", "/config",
                         "/shell", "/cmd", "/passwd", "/../"]
            for sus in suspicious:
                if sus.lower() in request.lower():
                    log_event("HTTP", attacker_ip, attacker_port,
                              f"SUSPICIOUS PATH detected: {sus}")

            # Check for credentials in POST body
            if "POST" in request and ("username" in request.lower() or
                                       "password" in request.lower() or
                                       "user=" in request.lower()):
                body = request.split("\r\n\r\n")[-1] if "\r\n\r\n" in request else ""
                if body:
                    log_event("HTTP", attacker_ip, attacker_port,
                              f"Credential attempt in POST: {body[:100]}")

        # Send a fake response - looks like a real server
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Server: Apache/2.4.41 (Ubuntu)\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n\r\n"
            "<html><head><title>Admin Panel</title></head>"
            "<body><h2>Login</h2>"
            "<form method='POST'>"
            "Username: <input name='user'><br>"
            "Password: <input type='password' name='pass'><br>"
            "<input type='submit' value='Login'>"
            "</form></body></html>"
        )
        conn.send(response.encode())

    except Exception:
        pass
    finally:
        conn.close()


def handle_ftp_client(conn, addr):
    """Handle a fake FTP connection."""
    attacker_ip = addr[0]
    attacker_port = addr[1]

    log_event("FTP", attacker_ip, attacker_port, "Connection established")

    try:
        # Send fake FTP banner
        conn.send(b"220 FTP Server Ready\r\n")

        while True:
            data = conn.recv(1024).decode("utf-8", errors="ignore").strip()
            if not data:
                break

            cmd = data.split(" ")[0].upper()
            args = " ".join(data.split(" ")[1:]) if " " in data else ""

            if cmd == "USER":
                log_event("FTP", attacker_ip, attacker_port, f"Username attempt: '{args}'")
                conn.send(b"331 Password required\r\n")

            elif cmd == "PASS":
                log_event("FTP", attacker_ip, attacker_port, f"Password attempt: '{args}'")
                conn.send(b"530 Login incorrect\r\n")
                break

            elif cmd == "QUIT":
                conn.send(b"221 Goodbye\r\n")
                break

            else:
                log_event("FTP", attacker_ip, attacker_port, f"Command: {data}")
                conn.send(b"500 Unknown command\r\n")

    except Exception:
        pass
    finally:
        conn.close()


def start_honeypot(service, port):
    """Start a honeypot server on the given port."""
    global running
    running = True

    handler_map = {
        "SSH":  handle_ssh_client,
        "HTTP": handle_http_client,
        "FTP":  handle_ftp_client,
    }

    handler = handler_map.get(service, handle_ssh_client)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        server.settimeout(1)

        print(f"\n  Honeypot started!")
        print(f"  Service : Fake {service} server")
        print(f"  Port    : {port}")
        print(f"  Logging : {LOG_FILE}")
        print(f"\n  Waiting for attackers... (Press Ctrl+C to stop)\n")
        print("  " + "-"*50)

        while running:
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=handler, args=(conn, addr))
                t.daemon = True
                t.start()
            except socket.timeout:
                continue
            except Exception:
                break

    except PermissionError:
        print(f"\n  Permission denied on port {port}.")
        print(f"  Try running VS Code as Administrator.")
        print(f"  Or use a port above 1024 (e.g. 2222 for SSH).")
    except OSError as e:
        print(f"\n  Could not start on port {port}: {e}")
        print(f"  The port may already be in use.")
    finally:
        running = False
        try:
            server.close()
        except:
            pass
        print("\n  Honeypot stopped.")


def view_log():
    """Display the attack log."""
    print("\n" + "="*55)
    print("  ATTACK LOG")
    print("="*55)

    if not attack_log:
        # Try reading from file
        if os.path.exists(LOG_FILE):
            print(f"  Reading from {LOG_FILE}:\n")
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
            if lines:
                for line in lines[-20:]:  # Show last 20
                    print(f"  {line.strip()}")
                print(f"\n  Total entries in file: {len(lines)}")
            else:
                print("  Log file is empty.")
        else:
            print("  No attacks recorded yet.")
            print("  Start a honeypot and wait for connections!")
        print("="*55)
        return

    print(f"  Total attacks this session: {len(attack_log)}\n")
    print(f"  {'TIME':<22} {'SERVICE':<8} {'IP':<18} MESSAGE")
    print("  " + "-"*70)

    for entry in attack_log[-20:]:
        print(f"  {entry['time']:<22} {entry['service']:<8} "
              f"{entry['ip']:<18} {entry['message']}")

    print("="*55)

    # Stats
    services = {}
    ips = {}
    for entry in attack_log:
        services[entry['service']] = services.get(entry['service'], 0) + 1
        ips[entry['ip']] = ips.get(entry['ip'], 0) + 1

    print("\n  Top Attacker IPs:")
    for ip, count in sorted(ips.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {ip:<20} {count} attempts")

    print("\n  By Service:")
    for svc, count in services.items():
        print(f"    {svc:<10} {count} events")
    print("="*55)


def clear_log():
    global attack_log
    attack_log = []
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    print("\n  Log cleared!")


def learn_mode():
    print("""
  HOW HONEYPOTS WORK
  ==================

  WHAT IS A HONEYPOT?
  A honeypot is a DECOY system designed to look
  like a real, valuable target to attract attackers.

  It has NO real data or value — its only purpose
  is to detect, track, and study attackers!

  HOW IT WORKS:
    1. You set up a fake server (SSH, HTTP, FTP)
    2. Attacker finds it and tries to break in
    3. Every action they take is silently logged
    4. You learn: their IP, tools, techniques
    5. You use that info to protect real systems

  TYPES OF HONEYPOTS:
    Low Interaction  -> Simulates services only
                        (like this project!)
    High Interaction -> Real OS, fully monitored
                        (used by big companies)
    Honeynets        -> Entire fake network of
                        honeypot machines

  REAL WORLD USE:
    - Banks use honeypots to detect hackers early
    - Governments use them to track cybercriminals
    - Security researchers use them to study malware
    - Companies use them to buy time and alert teams

  FAMOUS HONEYPOT TOOLS:
    Kippo / Cowrie  -> Fake SSH honeypots
    Dionaea         -> Catches malware samples
    Canary Tokens   -> Invisible tripwires in files

  WHAT YOU LEARN FROM ATTACKER DATA:
    - Which usernames/passwords they try (credential lists)
    - Which vulnerabilities they target first
    - Where attacks are coming from geographically
    - What tools and scripts they use

  This project simulates all three main honeypot
  types: SSH, HTTP, and FTP!
    """)


def main():
    display_banner()
    print("\n  TIP: Run VS Code as Administrator for ports below 1024")
    print("  Safe ports to use: 2222 (SSH), 8080 (HTTP), 2121 (FTP)")

    while True:
        display_menu()
        choice = input("\n  Choose an option (1-7): ").strip()

        if choice == "1":
            try:
                port = int(input("  Enter port (default 2222): ") or "2222")
            except ValueError:
                port = 2222
            start_honeypot("SSH", port)

        elif choice == "2":
            try:
                port = int(input("  Enter port (default 8080): ") or "8080")
            except ValueError:
                port = 8080
            start_honeypot("HTTP", port)

        elif choice == "3":
            try:
                port = int(input("  Enter port (default 2121): ") or "2121")
            except ValueError:
                port = 2121
            start_honeypot("FTP", port)

        elif choice == "4":
            view_log()

        elif choice == "5":
            clear_log()

        elif choice == "6":
            learn_mode()

        elif choice == "7":
            print("\n  Goodbye! Keep learning cybersecurity!\n")
            break

        else:
            print("\n  Invalid option. Please choose 1-7.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()