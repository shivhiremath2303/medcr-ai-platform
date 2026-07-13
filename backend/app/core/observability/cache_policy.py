from enum import IntEnum


class CacheTTL(IntEnum):
    """
    Standardized TTL policies for Enterprise Caching (Milestone 10.3.1).
    Values in seconds.
    """

    TINY = 60  # 1 minute (high frequency volatile data)
    SHORT = 300  # 5 minutes (AI responses, hot retrieval)
    MEDIUM = 3600  # 1 hour (Standard retrieval results)
    LONG = 86400  # 24 hours (Metadata, static configurations)
    EXTREME = 604800  # 1 week (Large document indices metadata)
