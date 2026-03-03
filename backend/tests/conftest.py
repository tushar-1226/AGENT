"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture
def sample_code():
    """Sample Python code for testing"""
    return """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
"""


@pytest.fixture
def sample_javascript():
    """Sample JavaScript code for testing"""
    return """
function calculateSum(numbers) {
    let total = 0;
    for (let num of numbers) {
        total += num;
    }
    return total;
}

const multiply = (a, b) => a * b;
"""
