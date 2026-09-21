import os
import socket
import threading
import time

from datetime import datetime

UE_NAME = os.environ["UE_NAME"]

PC5_SIM_HOST = os.getenv(
    "PC5_SIM_HOST",
    "pc5-sim",
)

PC5_SIM_PORT = int(
    os.getenv(
        "PC5_SIM_PORT",
        "8810",
    )
)

EXTERNAL_PORT = int(
    os.getenv(
        "EXTERNAL_PORT",
        "8809",
    )
)

IP_TTL = int(
    os.getenv(
        "IP_TTL",
        "255",
    )
)

external_ue_endpoint = None
endpoint_lock = threading.Lock()


def log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3]

    print(
        f"[{timestamp}] "
        f"[{UE_NAME.upper()}] "
        f"{message}",
        flush=True,
    )


external_sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
)

external_sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_TTL,
    IP_TTL,
)

external_sock.bind(
    ("0.0.0.0", EXTERNAL_PORT)
)


internal_sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
)

internal_sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_TTL,
    IP_TTL,
)

internal_sock.bind(
    ("0.0.0.0", 0)
)


def send_internal(payload):
    internal_sock.sendto(
        payload,
        (
            PC5_SIM_HOST,
            PC5_SIM_PORT,
        ),
    )


def register():
    """
    Registra el adapter en PC5-SIM.
    """

    packet = (
        b"REGISTER\0"
        + UE_NAME.encode()
    )

    send_internal(packet)

    log("registered with PC5-SIM")


def registration_loop():
    """
    Reenvía periódicamente el registro.

    Esto también permite que PC5-SIM reinicie
    sin perder permanentemente los adapters.
    """

    while True:
        register()
        time.sleep(5)


def external_receiver():
    global external_ue_endpoint

    while True:
        data, addr = external_sock.recvfrom(
            65535
        )

        with endpoint_lock:
            external_ue_endpoint = addr

        log(
            f"RX VM "
            f"{addr[0]}:{addr[1]} "
            f"{len(data)} bytes"
        )

        packet = (
            b"DATA\0"
            + UE_NAME.encode()
            + b"\0"
            + data
        )

        send_internal(packet)

        log(
            f"TX PC5-SIM "
            f"{PC5_SIM_HOST}:{PC5_SIM_PORT}"
        )


def internal_receiver():
    while True:
        data, addr = internal_sock.recvfrom(
            65535
        )

        with endpoint_lock:
            endpoint = external_ue_endpoint

        if endpoint is None:
            log(
                "DROP incoming PC5 data: "
                "VM endpoint unknown"
            )
            continue

        external_sock.sendto(
            data,
            endpoint,
        )

        log(
            f"TX VM "
            f"{endpoint[0]}:{endpoint[1]} "
            f"{len(data)} bytes"
        )


log(f"external UDP/{EXTERNAL_PORT}")
log(
    f"PC5-SIM "
    f"{PC5_SIM_HOST}:{PC5_SIM_PORT}"
)
log(f"TTL={IP_TTL}")

threading.Thread(
    target=registration_loop,
    daemon=True,
).start()

threading.Thread(
    target=external_receiver,
    daemon=True,
).start()

threading.Thread(
    target=internal_receiver,
    daemon=True,
).start()

threading.Event().wait()
