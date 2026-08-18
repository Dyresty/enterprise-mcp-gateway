import pytest

from app.retry.retry import RetryExecutor


def test_retry_succeeds_on_first_attempt():
    executor = RetryExecutor()

    calls = []

    def function():
        calls.append(1)
        return "success"

    result = executor.execute(
        function,
        max_retries=2,
    )

    assert result == "success"
    assert len(calls) == 1


def test_retry_succeeds_after_failure():
    executor = RetryExecutor()

    calls = []

    def function():
        calls.append(1)

        if len(calls) < 3:
            raise RuntimeError("temporary failure")

        return "success"

    result = executor.execute(
        function,
        max_retries=2,
        backoff_seconds=0,
    )

    assert result == "success"
    assert len(calls) == 3


def test_retry_exhausted():
    executor = RetryExecutor()

    calls = []

    def function():
        calls.append(1)
        raise RuntimeError("failure")

    with pytest.raises(
        RuntimeError,
        match="failure",
    ):
        executor.execute(
            function,
            max_retries=2,
            backoff_seconds=0,
        )

    assert len(calls) == 3


def test_zero_retries_means_single_attempt():
    executor = RetryExecutor()

    calls = []

    def function():
        calls.append(1)
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError):
        executor.execute(
            function,
            max_retries=0,
            backoff_seconds=0,
        )

    assert len(calls) == 1


def test_negative_retries_are_rejected():
    executor = RetryExecutor()

    with pytest.raises(
        ValueError,
        match="greater than or equal to zero",
    ):
        executor.execute(
            lambda: "success",
            max_retries=-1,
        )