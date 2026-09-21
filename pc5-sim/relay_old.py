import socket

LISTEN_PORT = 8809
UE_B_HOST = "ue-b"
UE_B_PORT = 8809
IP_TTL = 255

# Socket de recepción
rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx_sock.bind(("0.0.0.0", LISTEN_PORT))

# Socket de transmisión
tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MONP requiere TTL=255.
tx_sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_TTL,
    IP_TTL,
)

print(
    f"[PC5-SIM] Listening on UDP/{LISTEN_PORT}",
    flush=True,
)

print(
    f"[PC5-SIM] Forwarding to {UE_B_HOST}:{UE_B_PORT}",
    flush=True,
)

print(
    f"[PC5-SIM] TX IP TTL={IP_TTL}",
    flush=True,
)

while True:
    data, addr = rx_sock.recvfrom(65535)

    print(
        f"[PC5-SIM] RX from {addr}: "
        f"{data.decode(errors='replace')}",
        flush=True,
    )

    tx_sock.sendto(
        data,
        (UE_B_HOST, UE_B_PORT),
    )

    print(
        f"[PC5-SIM] TX to {UE_B_HOST}:{UE_B_PORT}",
        flush=True,
    )
