import pytest

from app.utils.split_list import split_list


@pytest.mark.parametrize(
    ("split_list_param", "output_len"),
    [
        ({"lst": [1, 2, 3], "chunk_size": 3}, 1),
        ({"lst": [1, 2, 3], "chunk_size": 2}, 2),
        ({"lst": [1, 2, 3], "chunk_size": 1}, 3),
    ],
)
def test_split_list(split_list_param, output_len: list[int]) -> None:
    split_list_res = list(split_list(**split_list_param))
    assert len(split_list_res) == output_len
