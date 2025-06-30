from scripts.kdp_publisher import KdpPublisher


class DummyPublisher(KdpPublisher):
    """
    Subclass to override the simulate_kdp_upload_process for testing.
    """

    def simulate_kdp_upload_process(self, book_metadata: dict):
        # Return a predictable structure for testing
        return {
            "success": True,
            "asin": "TESTASIN123",
            "title": book_metadata.get("title"),
            "operations_completed": 1,
        }


def test_upload_book_delegates_to_simulate(monkeypatch):
    # Prepare test metadata
    test_metadata = {"title": "Unit Test Book"}
    called = {}

    # Monkeypatch the simulate_kdp_upload_process method
    def fake_simulate(self, metadata):
        called["metadata"] = metadata
        return {"success": False, "error": "Simulated failure"}

    monkeypatch.setattr(KdpPublisher, "simulate_kdp_upload_process", fake_simulate)

    publisher = KdpPublisher()
    result = publisher.upload_book(test_metadata)

    # Assert that the result comes from our fake method
    assert result == {"success": False, "error": "Simulated failure"}
    # Assert that the method was called with our test metadata
    assert called.get("metadata") == test_metadata


def test_dummy_publisher_returns_expected():
    # Using DummyPublisher to test actual return structure
    dummy = DummyPublisher()
    metadata = {"title": "Dummy Book"}
    result = dummy.upload_book(metadata)

    assert result["success"] is True
    assert result["asin"] == "TESTASIN123"
    assert result["title"] == "Dummy Book"
    assert result["operations_completed"] == 1
