from collections.abc import Callable
from typing import Any

Node = Callable[[dict[str, str], dict[str, Any]], tuple[bool, dict]]
