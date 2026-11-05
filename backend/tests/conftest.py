"""
Pytest Test Fixtures
Provides test database sessions and mocked dataset samples.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.config import settings
from app.database import Base, get_db
from app.main import app

@pytest.fixture(scope="session")
def sample_dataframe():
    """Generates a clean synthetic classification dataframe for testing."""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "feature1": np.random.normal(10, 2, n),
        "feature2": np.random.uniform(1, 50, n),
        "category": np.random.choice(["A", "B", "C"], n),
        "target": np.random.choice([0, 1], n)
    })
    return df
