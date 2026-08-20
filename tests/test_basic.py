"""
PHASE 1: Learning pytest Basics
=================================

Before testing our real application, let's understand how pytest works
with two tiny examples.

TEACHING NOTES:

What is a test?
  A test is a function that checks whether code behaves correctly.
  If the code does what you expect → test PASSES.
  If the code does something wrong → test FAILS.

How does pytest discover tests?
  pytest automatically finds tests by looking for:
    1. Files named test_*.py or *_test.py
    2. Functions named test_*
    3. Classes named Test*

The AAA Pattern (Arrange, Act, Assert):
  Every good test follows three steps:
    - Arrange: Set up the data and conditions.
    - Act:     Call the code being tested.
    - Assert:  Verify the result is what you expected.

HOW TO RUN:
  Run all tests:             pytest -v
  Run this file only:        pytest tests/test_basic.py -v
  Run a single test:         pytest tests/test_basic.py::test_add_two_positive_numbers -v
"""


# A simple function to test (in real life, this would be in your app code)
def add(a, b):
    return a + b


# ─── Test 1: A passing test ─────────────────────────────────────────────

def test_add_two_positive_numbers():
    """
    Arrange: Define inputs (2 and 3)
    Act:     Call add(2, 3)
    Assert:  Check that the result equals 5
    """
    # Arrange
    a = 2
    b = 3

    # Act
    result = add(a, b)

    # Assert — if this is True, the test PASSES. If False, it FAILS.
    assert result == 5


# ─── Test 2: Edge cases ─────────────────────────────────────────────────

def test_add_negative_numbers():
    """Tests that add works with negative numbers."""
    assert add(-1, -1) == -2


def test_add_zero():
    """Tests the identity property: adding zero changes nothing."""
    assert add(5, 0) == 5
