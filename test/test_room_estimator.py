from positioning.room_estimator import RoomEstimator

def test_empty_snapshot_returns_none(room_estimator: RoomEstimator):
    candidate = room_estimator.estimate({})

    assert candidate is None

def test_node_room_mapping(room_estimator: RoomEstimator):
    candidate = room_estimator.estimate({"kitchen-esp": -60})

    assert candidate == "kitchen"

def test_strongest_signal_leads_to_candidate(room_estimator: RoomEstimator):
    candidate = room_estimator.estimate({"kitchen-esp": -60, "bed-esp": -40})

    assert candidate == "bedroom"

def test_multiple_nodes_in_room_returns_room(room_estimator: RoomEstimator):
    candidate = room_estimator.estimate({"bed-esp": -60, "wardrobe-esp": -40})

    assert candidate == "bedroom"

def test_strongest_signal_lower_than_min_rssi_returns_none(room_estimator: RoomEstimator):
    candidate = room_estimator.estimate({"kitchen-esp": -91, "bed-esp": -98})

    assert candidate is None



