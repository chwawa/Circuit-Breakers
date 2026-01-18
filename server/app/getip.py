import socket

def get_local_ip():
    # Create a dummy socket to connect to an external address
    # This doesn't send data but is used to find the IP used for outbound connections
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a reliable external IP (e.g., Google's DNS server)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(f"Server Local IP Address: {get_local_ip()}")