"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


# Create a test client instance
client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        """Test that the root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0
        
        # Verify activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_contains_expected_fields(self):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert isinstance(activity, dict)
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_activity_not_found(self):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_activities(self):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"
        
        # First sign up
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Basketball Team" in data["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self):
        """Test unregister fails if student is not signed up"""
        response = client.delete(
            "/activities/Soccer Club/unregister",
            params={"email": "notsigndup@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_and_resign_up(self):
        """Test that a student can unregister and then sign up again"""
        email = "resign@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        
        # Unregister
        response1 = client.delete(
            "/activities/Drama Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
