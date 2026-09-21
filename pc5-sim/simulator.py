import socket

from datetime import datetime

LISTEN_PORT = 8810
IP_TTL = 255

ue_endpoints = {}


def log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3]

    print(
        f"[{timestamp}] "
        f"[PC5-SIM] "
        f"{message}",
        flush=True,
    )


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
)

sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_TTL,
    IP_TTL,
)

sock.bind(
    ("0.0.0.0", LISTEN_PORT)
)

log(
    f"Listening internal UDP/{LISTEN_PORT}"
)
log(f"TTL={IP_TTL}")


while True:
    packet, addr = sock.recvfrom(65535)

    parts = packet.split(
        b"\0",
        2,
    )

    message_type = parts[0]

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    if message_type == b"REGISTER":

        if len(parts) < 2:
            log("DROP malformed REGISTER")
            continue

        ue_name = parts[1].decode()
        
        previous_endpoint = ue_endpoints.get(ue_name)

        ue_endpoints[ue_name] = addr

        if previous_endpoint != addr:
            log(
                f"REGISTER {ue_name} "
                f"{addr[0]}:{addr[1]}"
            )

        continue

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    if message_type != b"DATA":

        log(
            f"DROP unknown message type "
            f"{message_type!r}"
        )

        continue

    if len(parts) != 3:
        log("DROP malformed DATA")
        continue

    source = parts[1].decode()
    payload = parts[2]

    ue_endpoints[source] = addr

    if source == "ue-a":
        destination = "ue-b"

    elif source == "ue-b":
        destination = "ue-a"

    else:
        log(
            f"DROP unknown UE {source}"
        )
        continue

    log(
        f"RX {source} "
        f"{len(payload)} bytes"
    )

    destination_endpoint = (
        ue_endpoints.get(destination)
    )

    if destination_endpoint is None:
        log(
            f"DROP {source}->{destination}: "
            "destination not registered"
        )
        continue

    sock.sendto(
        payload,
        destination_endpoint,
    )

    log(
        f"TX {source}->{destination} "
        f"{destination_endpoint[0]}:"
        f"{destination_endpoint[1]}"
    )
