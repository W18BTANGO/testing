"""
End-to-end tests for the preprocessing and analytics workflow.
These tests verify that the entire system works together correctly.
"""
import pytest
import requests

# Define base URLs for services - update with actual endpoints when deployed
PREPROCESSING_URL = "http://preprocessing-681292228.ap-southeast-2.elb.amazonaws.com/"
ANALYTICS_URL = "http://alb8-2127494217.ap-southeast-2.elb.amazonaws.com/"


def test_end_to_end_workflow():
    """Test the complete data processing pipeline from preprocessing to analytics."""
    # Step 1: Send data to preprocessing service
    preprocessing_payload = {
        "json_data": {
            "events": [
                {"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000, "suburb": "SuburbA"}},
                {"time_object": {"timestamp": "2025-01-02T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 600000, "suburb": "SuburbB"}},
                {"time_object": {"timestamp": "2025-01-03T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 700000, "suburb": "SuburbA"}},
            ]
        },
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    preprocessing_response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert preprocessing_response.status_code == 200
    filtered_data = preprocessing_response.json().get("filtered_data")
    assert filtered_data is not None
    assert len(filtered_data) == 3  # Ensure all events are included after filtering

    # Step 2: Send filtered data to analytics service for predictions
    analytics_payload = {
        "data": filtered_data,
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000, 600000, 700000],
    }
    analytics_response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert analytics_response.status_code == 200
    predictions = analytics_response.json().get("prediction")
    assert predictions is not None
    assert len(predictions) == 3  # Ensure predictions are returned for all x_values

    # Step 3: Verify additional analytics (e.g., average price by suburb)
    analytics_suburb_payload = filtered_data
    suburb_response = requests.post(f"{ANALYTICS_URL}/average-price-by-suburb", json=analytics_suburb_payload)
    assert suburb_response.status_code == 200
    average_prices = suburb_response.json().get("average_prices")
    assert average_prices is not None
    assert "SuburbA" in average_prices
    assert "SuburbB" in average_prices
    assert average_prices["SuburbA"] == 600000  # Average of 500000 and 700000
    assert average_prices["SuburbB"] == 600000  # Single event with price 600000


def test_empty_preprocessing_data():
    """Test preprocessing service with empty data."""
    preprocessing_payload = {
        "json_data": {"events": []},
        "event_type": ["sale"],
        "filters": [{"attribute": "suburb", "values": ["SuburbA", "SuburbB"]}],
    }
    response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert response.status_code == 200
    filtered_data = response.json().get("filtered_data")
    assert filtered_data == []  # Expect no data after filtering


def test_invalid_preprocessing_payload():
    """Test preprocessing service with invalid payload."""
    preprocessing_payload = {"invalid_key": "invalid_value"}
    response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=preprocessing_payload)
    assert response.status_code == 422


def test_empty_analytics_data():
    """Test analytics service with empty data."""
    analytics_payload = {
        "data": [],
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000, 600000],
    }
    response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert response.status_code == 400
    assert "Found array with 0 sample(s)" in response.json().get("detail", "")


def test_mismatched_x_y_data_lengths():
    """Test analytics service with mismatched x and y data lengths."""
    analytics_payload = {
        "data": [
            {"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000}},
            {"time_object": {"timestamp": "2025-01-02T00:00:00Z"}, "event_type": "sale", "attribute": {"price": None}},
        ],
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000],
    }
    response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert response.status_code == 400
    assert "NaN" in response.json().get("detail", "")


def test_invalid_analytics_payload():
    """Test analytics service with invalid payload."""
    analytics_payload = {"invalid_key": "invalid_value"}
    response = requests.post(f"{ANALYTICS_URL}/predict", json=analytics_payload)
    assert response.status_code == 422
