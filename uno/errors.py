import logging

logger = logging.getLogger(__name__)


class EmptyDeckError(Exception):
    logger.exception("Empty deck exception.")
    pass


class WrongCardError(Exception):
    logger.exception("Wrong card exception: selected card cannot be played.")
    pass
