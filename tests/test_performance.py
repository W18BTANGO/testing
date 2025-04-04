import requests
import time

PREPROCESSING_URL = "http://preprocessing-681292228.ap-southeast-2.elb.amazonaws.com/"
ANALYTICS_URL = "http://alb8-2127494217.ap-southeast-2.elb.amazonaws.com/"

def test_preprocessing_performance():
    """Test preprocessing service response time."""
    payload = {
        "json_data": {
            "events": [{"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000}}],
        },
        "event_type": ["sale"],
    }
    start_time = time.time()
    response = requests.post(f"{PREPROCESSING_URL}/filter-data", json=payload)
    end_time = time.time()
    assert response.status_code == 200
    assert (end_time - start_time) < 1  # Ensure response time is under 1 second

def test_analytics_performance():
    """Test analytics service response time."""
    payload = {
        "data": [{"time_object": {"timestamp": "2025-01-01T00:00:00Z"}, "event_type": "sale", "attribute": {"price": 500000}}],
        "x_attribute": "price",
        "y_attribute": "price",
        "x_values": [500000],
    }
    start_time = time.time()
    response = requests.post(f"{ANALYTICS_URL}/predict", json=payload)
    end_time = time.time()
    assert response.status_code == 200
    assert (end_time - start_time) < 1  # Ensure response time is under 1 second
