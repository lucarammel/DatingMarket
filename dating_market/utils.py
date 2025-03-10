import functools
import time


def timeit(func):
    """Decorator to measure the execution time"""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Called {func.__name__} with args={args}, kwargs={kwargs}")  # Debugging
        start_time = time.perf_counter()
        result = func(self, *args, **kwargs)
        end_time = time.perf_counter()
        print(
            f"{self.__class__.__name__}.{func.__name__} executed in {end_time - start_time:.6f} seconds"
        )
        return result

    return wrapper
