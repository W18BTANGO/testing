import requests

PREPROCESSING_URL = "http://preprocessing-681292228.ap-southeast-2.elb.amazonaws.com/"
ANALYTICS_URL = "http://alb8-2127494217.ap-southeast-2.elb.amazonaws.com/"

def test_reliability():
    """Test reliability of preprocessing and analytics services."""
    for _ in range(1000):  # Simulate 1000 continuous requests
        preprocessing_response = requests.get(f"{PREPROCESSING_URL}/")
        assert preprocessing_response.status_code == 200

        analytics_response = requests.get(f"{ANALYTICS_URL}/")
        assert analytics_response.status_code == 200
