import paypalrestsdk
import logging

paypalrestsdk.configure({
    "mode": "sandbox",  # de prueba
    "client_id": "AVyG7ER0Urrx9xXZhQLt4R1URoRdbSbugfFUnLQTJWm-DBFUhdYXe8fR4Mm6JRDpvGdlSg86laAZ2ZTW",
    "client_secret": "EDH3Xylb54eEn_86Y4vwCxvRCLfJLDRatyqJrfgNbYibZU1yWkeqj6AM4NvQBI3ufQX-j29SqhU36B7i"
})

logging.basicConfig(level=logging.INFO)


