"""
E-Botar Lite — Core Algorithm Helpers
Includes: Cryptographic algorithms (SHA-256 hash chains, hashes),
Aggregation (vote tallies, groupings), Sorting, Searching, Memoization.
"""

from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import base64
import hashlib


class CryptographicAlgorithm:
    """Cryptographic primitives for voting ledger integrity and receipt hashing."""

    @staticmethod
    def sha256_hash(data: Union[str, bytes]) -> str:
        """Compute SHA-256 hex digest."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_chain_link(previous_hash: str, block_data: str) -> str:
        """Generate next hash in blockchain ledger."""
        payload = f"{previous_hash}{block_data}"
        return CryptographicAlgorithm.sha256_hash(payload)


class AggregationAlgorithm:
    """Group-by-key aggregation for vote counts and statistics."""

    @staticmethod
    def aggregate(
        items: Iterable[Any],
        key_func: Callable[[Any], Any],
        value_func: Optional[Callable[[Any], Any]] = None,
        operation: str = "count",
    ) -> Dict[Any, Any]:
        result = defaultdict(
            lambda: {
                "count": 0,
                "sum": 0,
                "values": [],
                "items": [],
            }
        )

        for item in items:
            category = key_func(item)
            result[category]["count"] += 1
            result[category]["items"].append(item)

            if value_func and operation in ("sum", "avg", "min", "max"):
                value = value_func(item)
                try:
                    value = float(value)
                    result[category]["sum"] += value
                    result[category]["values"].append(value)
                except (ValueError, TypeError):
                    pass

        final_result: Dict[Any, Any] = {}
        for category, data in result.items():
            if operation == "count":
                final_result[category] = data["count"]
            elif operation == "sum":
                final_result[category] = data["sum"]
            elif operation == "avg":
                final_result[category] = (
                    data["sum"] / data["count"] if data["count"] > 0 else 0
                )
            elif operation == "min":
                final_result[category] = min(data["values"]) if data["values"] else None
            elif operation == "max":
                final_result[category] = max(data["values"]) if data["values"] else None
            elif operation == "list":
                final_result[category] = data["items"]
            elif operation == "set":
                final_result[category] = list(set(data["items"]))
            else:
                final_result[category] = data

        return final_result


class SortingAlgorithm:
    """Quicksort implementation for candidate rankings."""

    @staticmethod
    def quicksort(arr: List[Any], key: Optional[Callable] = None, reverse: bool = False) -> List[Any]:
        if len(arr) <= 1:
            return arr.copy()
        
        def get_val(item):
            return key(item) if key else item

        pivot = arr[len(arr) // 2]
        pivot_val = get_val(pivot)

        left = [x for x in arr if (get_val(x) > pivot_val if reverse else get_val(x) < pivot_val)]
        middle = [x for x in arr if get_val(x) == pivot_val]
        right = [x for x in arr if (get_val(x) < pivot_val if reverse else get_val(x) > pivot_val)]

        return SortingAlgorithm.quicksort(left, key, reverse) + middle + SortingAlgorithm.quicksort(right, key, reverse)


class SearchingAlgorithm:
    """Binary search for sorted data."""

    @staticmethod
    def binary_search(arr: List[Any], target: Any, key: Optional[Callable] = None) -> int:
        if not arr:
            return -1
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            val = key(arr[mid]) if key else arr[mid]
            if val == target:
                return mid
            elif val < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1


class MemoizationAlgorithm:
    """In-memory cache helper."""
    _cache = {}

    @classmethod
    def memoize(cls, key: str, compute_func: Callable[[], Any], ttl_seconds: Optional[int] = None) -> Any:
        if key in cls._cache:
            return cls._cache[key]
        val = compute_func()
        cls._cache[key] = val
        return val

    @classmethod
    def invalidate(cls, key_prefix: str = ""):
        if not key_prefix:
            cls._cache.clear()
        else:
            keys = [k for k in cls._cache if k.startswith(key_prefix)]
            for k in keys:
                del cls._cache[k]
