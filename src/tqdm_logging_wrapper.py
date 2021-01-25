"""Wrap standard-library logging to support TQDM progress-bars."""

import logging
import contextlib
import typing as t

if t.TYPE_CHECKING:
    import tqdm


class _StreamHandlerWrapper:
    def __init__(self, handler: logging.StreamHandler, tqdm_iter: "tqdm.tqdm"):
        self.handler = handler
        self.stream = tqdm_iter

    def __getattr__(self, item):
        return getattr(self.handler, item)

    def emit(self, record: logging.LogRecord) -> None:
        if isinstance(self.handler, _StreamHandlerWrapper):
            self.handler.emit(record)
        else:
            msg = self.handler.format(record)
            self.stream.write(msg, file=self.handler.stream)

    handle = logging.Handler.handle


def _get_handlers(
    logger: logging.Logger,
) -> t.Generator[t.Tuple[int, logging.Handler, t.List[logging.Handler]], None, None]:
    while logger:
        for i, handler in enumerate(logger.handlers):
            yield i, handler, logger.handlers
        logger = logger.parent if logger.propagate else None


def _is_tty_stream_handler(handler: logging.Handler) -> bool:
    if isinstance(handler, _StreamHandlerWrapper):
        return _is_tty_stream_handler(handler.handler)
    return (
        hasattr(handler, "stream")
        and hasattr(handler.stream, "isatty")
        and handler.stream.isatty()
    )


@contextlib.contextmanager
def wrap_logging_for_tqdm(
    tqdm_iter: "tqdm.tqdm",
    logger: logging.Logger = logging.root,
) -> t.Generator[None, None, None]:
    """Wrap logging to support TQDM progress-bar.

    Args:
        tqdm_iter: TQDM iterable instance
        logger: logger to wrap effective handlers of
    """

    for i, handler, handlers in _get_handlers(logger):
        if _is_tty_stream_handler(handler):
            handlers[i] = _StreamHandlerWrapper(handler, tqdm_iter)
    try:
        yield
    finally:
        for i, handler, handlers in _get_handlers(logger):
            if isinstance(handler, _StreamHandlerWrapper):
                handlers[i] = handler.handler
