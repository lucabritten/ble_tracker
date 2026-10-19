from statistics import median


from positioning.rssi_window import RssiWindow
from conftest import MAX_AGE, WINDOW_SIZE


def test_empty_window_returns_empty_dict(rssi_window: RssiWindow):
    assert rssi_window.snapshot(10) == {}

def test_single_value_given_returns_value(rssi_window: RssiWindow):
    rssi_window.add("bedroom", -50, 9)
    snapshot = rssi_window.snapshot(10)

    assert "bedroom" in snapshot.keys()
    assert snapshot["bedroom"] == -50

def test_multiple_value_given_returns_median(rssi_window: RssiWindow):
    val_a = -60
    val_b = -10
    val_c = -80
    rssi_window.add("bedroom", val_a, 9)
    rssi_window.add("bedroom", val_b, 10)
    rssi_window.add("bedroom", val_c, 11)

    snapshot = rssi_window.snapshot(12)

    assert "bedroom" in snapshot.keys()
    assert snapshot["bedroom"] == median([val_a,val_b, val_c])

def test_oldest_value_dropped_when_more_values_than_window_size(rssi_window: RssiWindow):
    values = list(range(-100, -100 + WINDOW_SIZE + 1))

    for time, value in enumerate(values):
        rssi_window.add("bedroom", value, time)

    snapshot = rssi_window.snapshot(len(values))
    expected_window_content = values[-WINDOW_SIZE:]

    assert snapshot["bedroom"] == median(expected_window_content)

def test_node_with_to_old_values_not_returned(rssi_window: RssiWindow):
    time_a = 1
    rssi_window.add("bedroom", -50, 1)

    snapshot = rssi_window.snapshot(time_a + MAX_AGE + 1)
    assert snapshot == {}

def test_outdated_nodes_are_not_returned(rssi_window: RssiWindow):
    rssi_window.add("bedroom", -50, 0)
    rssi_window.add("living_room", -50, MAX_AGE)

    snapshot = rssi_window.snapshot(MAX_AGE + 1)
    assert len(snapshot.keys()) == 1
    assert snapshot["living_room"] == -50

def test_multiple_nodes_are_independent(rssi_window: RssiWindow):
    rssi_window.add("bedroom", -10, 0)
    rssi_window.add("bedroom", -20, 1)
    rssi_window.add("bedroom", -30, 2)

    rssi_window.add("kitchen", -50, 0)
    rssi_window.add("kitchen", -60, 1)
    rssi_window.add("kitchen", -70, 2)

    snapshot = rssi_window.snapshot(3)
    assert len(snapshot.keys()) == 2
    assert snapshot["bedroom"] == -20
    assert snapshot["kitchen"] == -60

def test_outdated_node_is_reactivated_when_new_value(rssi_window: RssiWindow):
    rssi_window.add("bedroom", -50, 0)

    snapshot = rssi_window.snapshot(1)
    assert "bedroom" in snapshot.keys()

    snapshot = rssi_window.snapshot(MAX_AGE + 1)
    assert "bedroom" not in snapshot.keys()

    rssi_window.add("bedroom", -50, MAX_AGE + 2)
    snapshot = rssi_window.snapshot(MAX_AGE + 3)
    assert "bedroom" in snapshot.keys()