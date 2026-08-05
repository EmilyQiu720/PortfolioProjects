from app.drift import population_stability_index


def test_psi_is_zero_for_identical_distribution():
    values = [1, 2, 3, 4, 5, 6, 7, 8]
    assert population_stability_index(values, values) == 0


def test_psi_increases_for_shifted_distribution():
    reference = [1, 2, 3, 4, 5, 6, 7, 8]
    current = [80, 82, 84, 86, 88, 90, 92, 94]
    assert population_stability_index(reference, current) > 0

