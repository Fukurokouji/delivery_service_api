def split_list(lst: list, chunk_size: int) -> list[list[int]]:
    """function for splitting batch of data to chunks with some size"""
    for i in range(0, len(lst), chunk_size):
        # fmt: off
        yield lst[i: i + chunk_size]
