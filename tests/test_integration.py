"""
Integration tests for preprocessing and analytics services.
These tests verify that the individual services work correctly with their dependencies.
"""
import pytest
import requests

# Define base URLs for services - update with actual endpoints when deployed
PREPROCESSING_URL = "http://preprocessing-681292228.ap-southeast-2.elb.amazonaws.com/"
ANALYTICS_URL = "http://alb8-2127494217.ap-southeast-2.elb.amazonaws.com/"


def test_preprocessing_health():
    """Test if preprocessing service is healthy."""
    response = requests.get(f"{PREPROCESSING_URL}/")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_analytics_health():
    """Test if analytics service is healthy."""
    response = requests.get(f"{ANALYTICS_URL}/")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_preprocessing_to_analytics_integration():
    """Test the integration between preprocessing and analytics services."""
    # Step 1: Send data to preprocessing service
    preprocessing_payload = {
        "json_data": {
            "events": [
                {"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000, "suburb": "SuburbA"}},
                {"time_object": {"timestamp": "2025-01-02T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 600000, "suburb": "SuburbB"}},
            ]
        },
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    preprocessing_response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert preprocessing_response.status_code == 200
    filtered_data = preprocessing_response.json().get("filtered_data")
    assert filtered_data is not None

    # Step 2: Send filtered data to analytics service
    analytics_payload = {
        "data": filtered_data,
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000, 600000],
    }
    analytics_response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert analytics_response.status_code == 200
    predictions = analytics_response.json().get("prediction")
    assert predictions is not None
    assert len(predictions) == 2


def test_preprocessing_empty_events_to_analytics():
    """Test integration when preprocessing returns no filtered data."""
    preprocessing_payload = {
        "json_data": {"events": []},
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    preprocessing_response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert preprocessing_response.status_code == 200
    filtered_data = preprocessing_response.json().get("filtered_data")
    assert filtered_data == []  # Expect no data after filtering

    analytics_payload = {
        "data": filtered_data,
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000, 600000],
    }
    analytics_response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert analytics_response.status_code == 400
    assert "Found array with 0 sample(s)" in analytics_response.json().get("detail", "")


def test_preprocessing_invalid_data_to_analytics():
    """Test integration when preprocessing returns invalid data."""
    preprocessing_payload = {
        "json_data": {
            "events": [
                {"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": None}},
                {"time_object": {"timestamp": "2025-01-02T00:00:00Z"}, "event_type": "sale", "attribute": {"price": None}},
            ]
        },
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    preprocessing_response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert preprocessing_response.status_code == 200
    filtered_data = preprocessing_response.json().get("filtered_data")
    assert filtered_data == []

    analytics_payload = {
        "data": filtered_data,
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000, 600000],
    }
    analytics_response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert analytics_response.status_code == 400
    assert "Found array with 0 sample(s)" in analytics_response.json().get("detail", "")


def test_preprocessing_partial_valid_data_to_analytics():
    """Test integration when preprocessing returns partially valid data."""
    preprocessing_payload = {
        "json_data": {
            "events": [
                {"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000}},
                {"time_object": {"timestamp": "2025-01-02T00:00:00Z"}, "event_type": "sale", "attribute": {"price": None}},
            ]
        },
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    preprocessing_response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert preprocessing_response.status_code == 200
    filtered_data = preprocessing_response.json().get("filtered_data")
    assert filtered_data is not None

    analytics_payload = {
        "data": filtered_data,
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000],
    }
    analytics_response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert analytics_response.status_code == 400
    predictions = analytics_response.json().get("prediction")
    assert predictions is None
