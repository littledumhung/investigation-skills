import pytest
from scripts.temporal_checker import normalize, temporal_status

def test_unknown_not_fabricated(): assert normalize(None) is None
def test_as_of():
    assert temporal_status({'published_at':'2027-01-01'},'2026-10-30')=='POST_CUTOFF'
def test_expiry():
    assert temporal_status({'published_at':'2020-01-01','effective_until':'2026-01-01'},'2026-10-30')=='EXPIRED'
def test_naive_timestamp():
    with pytest.raises(ValueError): normalize('2026-10-30T12:00:00')
