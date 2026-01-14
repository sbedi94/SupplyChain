# app/tools/cache_tools.py

_cached_data = None

def save_cached_data(data):
    """Save data to in-memory cache"""
    global _cached_data
    _cached_data = data

def load_cached_data():
    """Load data from in-memory cache"""
    return _cached_data
