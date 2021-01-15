# TQDM logging wrapper
Wrap standard-library logging to support TQDM progress-bars.

## Installation
```bash
pip install tqdm-logging-wrapper
```

## Usage
```python
import logging

import tqdm
import tqdm_logging_wrapper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

items = [1, 2, 3]
items_iter = tqdm.tqdm(items)
logger.info(f"Items: {items}")
with tqdm_logging_wrapper.wrap_logging_for_tqdm(items_iter), items_iter:
    for item in items_iter:
        logger.info(f"Item: {item}")
logger.info(f"Items: {items}")
```
