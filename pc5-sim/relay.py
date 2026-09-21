import socket

LISTEN_PORT = 8809
UE_B_HOST = "ue-b"
UE_B_PORT = 8809
IP_TTL = 255

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_TTL,
    IP_TTL,
)

sock.bind(("0.0.0.0", LISTEN_PORT))

print(f"[PC5-SIM] Listening on UDP/{LISTEN_PORT}", flush=True)
print(f"[PC5-SIM] IP TTL={IP_TTL}", flush=True)
print(f"[PC5-SIM] Forwarding to {UE_B_HOST}:{UE_B_PORT}", flush=True)

while True:
    data, addr = sock.recvfrom(65535)

    print(
        f"[PC5-SIM] RX from {addr}: "
        f"{data.decode(errors='replace')}",
        flush=True,
    )

    sock.sendto(
        data,
        (UE_B_HOST, UE_B_PORT),
    )

    print(
        f"[PC5-SIM] TX from {sock.getsockname()[1]} "
        f"to {UE_B_HOST}:{UE_B_PORT}",
        flush=True,
    )
