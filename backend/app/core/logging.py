"""Configurazione del logging applicativo."""

import logging


def configure_logging() -> None:
    """Configura il logging principale dell'applicazione."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
