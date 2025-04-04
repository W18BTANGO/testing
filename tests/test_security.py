import requests

PREPROCESSING_URL = "http://preprocessing-681292228.ap-southeast-2.elb.amazonaws.com/"
ANALYTICS_URL = "http://alb8-2127494217.ap-southeast-2.elb.amazonaws.com/"

def test_public_accessibility():
    """Test public accessibility of preprocessing and analytics services."""
    preprocessing_response = requests.get(f"{PREPROCESSING_URL}/")
    assert preprocessing_response.status_code == 200
    assert preprocessing_response.json().get("status") == "healthy"

    analytics_response = requests.get(f"{ANALYTICS_URL}/")
    assert analytics_response.status_code == 200
    assert analytics_response.json().get("status") == "healthy"
