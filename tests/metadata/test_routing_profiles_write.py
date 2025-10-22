"""
Tests for routing profiles write operations (PUT/POST)

This module tests the write operations for routing profiles:
- import_routing_plan (PUT) - Import a new routing plan
- force_import_routing_plan (PUT) - Force import/overwrite existing plan
- start_routing_plan (POST) - Start a routing plan for a resource

Tests include both mocked tests (fast, for CI/CD) and real API tests (marked with uses_real_data).
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE


class TestRoutingProfileWriteMocked:
    """Mocked tests for routing profile write operations"""

    @pytest.fixture
    def ofsc_instance(self):
        """Create OFSC instance for testing"""
        return OFSC(
            clientID="test_client",
            secret="test_secret",
            companyName="test_company"
        )

    @pytest.fixture
    def sample_plan_data(self):
        """Load sample plan data from saved responses"""
        response_file = Path("tests/saved_responses/routing_profiles/export_routing_plan_actual_data.json")
        with open(response_file, "r") as f:
            data = json.load(f)
        return data["response_data"]

    @pytest.fixture
    def mock_import_409_response(self):
        """Mock 409 response for existing plan"""
        return {
            "status_code": 409,
            "json_data": {
                "title": "Fail",
                "status": "409",
                "force": "required",
                "detail": "The routing plan already exist."
            }
        }

    @pytest.fixture
    def mock_import_200_response(self):
        """Mock 200 response for successful import"""
        return {
            "status_code": 200,
            "json_data": {
                "title": "Ok",
                "status": "200",
                "detail": "The routing plan was successfully imported."
            }
        }

    @pytest.fixture
    def mock_force_import_200_response(self):
        """Mock 200 response for successful force import"""
        return {
            "status_code": 200,
            "json_data": {
                "title": "Ok",
                "status": "200",
                "detail": "The routing plan was successfully imported."
            }
        }

    @pytest.fixture
    def mock_start_200_response(self):
        """Mock 200 response for successful start"""
        return {
            "status_code": 200,
            "json_data": {
                "title": "Ok",
                "status": "200",
                "detail": "The routing plan was successfully started."
            }
        }

    @pytest.fixture
    def mock_start_404_response(self):
        """Mock 404 response for invalid resource"""
        return {
            "status_code": 404,
            "json_data": {
                "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5",
                "title": "Not Found",
                "status": "404",
                "detail": "Resource 'INVALID_RESOURCE' not found"
            }
        }

    # Import Routing Plan Tests

    def test_import_routing_plan_409_conflict(self, ofsc_instance, sample_plan_data, mock_import_409_response):
        """Test import routing plan returns 409 when plan already exists"""
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = mock_import_409_response["status_code"]
            mock_response.json.return_value = mock_import_409_response["json_data"]
            mock_response.text = json.dumps(mock_import_409_response["json_data"])
            mock_put.return_value = mock_response

            # Convert plan data to JSON bytes (as implementation will do)
            plan_json = json.dumps(sample_plan_data)
            plan_bytes = plan_json.encode('utf-8')

            response = ofsc_instance.metadata.import_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 409
            data = response.json()
            assert data["status"] == "409"
            assert data["force"] == "required"
            assert "already exist" in data["detail"]

    def test_import_routing_plan_200_success(self, ofsc_instance, sample_plan_data, mock_import_200_response):
        """Test import routing plan returns 200 for new plan"""
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = mock_import_200_response["status_code"]
            mock_response.json.return_value = mock_import_200_response["json_data"]
            mock_response.text = json.dumps(mock_import_200_response["json_data"])
            mock_put.return_value = mock_response

            plan_json = json.dumps(sample_plan_data)
            plan_bytes = plan_json.encode('utf-8')

            response = ofsc_instance.metadata.import_routing_plan(
                profile_label="NewProfile",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "200"
            assert "successfully imported" in data["detail"]

    # Force Import Routing Plan Tests

    def test_force_import_routing_plan_200_success(self, ofsc_instance, sample_plan_data, mock_force_import_200_response):
        """Test force import routing plan returns 200 on success"""
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = mock_force_import_200_response["status_code"]
            mock_response.json.return_value = mock_force_import_200_response["json_data"]
            mock_response.text = json.dumps(mock_force_import_200_response["json_data"])
            mock_put.return_value = mock_response

            plan_json = json.dumps(sample_plan_data)
            plan_bytes = plan_json.encode('utf-8')

            response = ofsc_instance.metadata.force_import_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "200"
            assert "successfully imported" in data["detail"]

    def test_force_import_overrides_existing_plan(self, ofsc_instance, sample_plan_data, mock_force_import_200_response):
        """Test force import can override existing plan"""
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_force_import_200_response["json_data"]
            mock_response.text = json.dumps(mock_force_import_200_response["json_data"])
            mock_put.return_value = mock_response

            plan_json = json.dumps(sample_plan_data)
            plan_bytes = plan_json.encode('utf-8')

            # Should succeed even if plan exists
            response = ofsc_instance.metadata.force_import_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_data=plan_bytes,
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 200
            # Verify the URL used forceImport
            call_args = mock_put.call_args
            assert "forceImport" in call_args[0][0]

    # Start Routing Plan Tests

    def test_start_routing_plan_200_success(self, ofsc_instance, mock_start_200_response):
        """Test start routing plan returns 200 on success"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = mock_start_200_response["status_code"]
            mock_response.json.return_value = mock_start_200_response["json_data"]
            mock_response.text = json.dumps(mock_start_200_response["json_data"])
            mock_post.return_value = mock_response

            response = ofsc_instance.metadata.start_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_label="Optimization",
                resource_external_id="TEST_RESOURCE",
                date="2025-10-23",
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "200"
            assert "successfully started" in data["detail"]

    def test_start_routing_plan_404_invalid_resource(self, ofsc_instance, mock_start_404_response):
        """Test start routing plan returns 404 for invalid resource"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = mock_start_404_response["status_code"]
            mock_response.json.return_value = mock_start_404_response["json_data"]
            mock_response.text = json.dumps(mock_start_404_response["json_data"])
            mock_post.return_value = mock_response

            response = ofsc_instance.metadata.start_routing_plan(
                profile_label="MaintenanceRoutingProfile",
                plan_label="Optimization",
                resource_external_id="INVALID_RESOURCE",
                date="2025-10-23",
                response_type=FULL_RESPONSE
            )

            assert response.status_code == 404
            data = response.json()
            assert data["status"] == "404"
            assert "not found" in data["detail"].lower()

    def test_start_routing_plan_url_encoding(self, ofsc_instance, mock_start_200_response):
        """Test start routing plan properly encodes URL parameters"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_start_200_response["json_data"]
            mock_response.text = json.dumps(mock_start_200_response["json_data"])
            mock_post.return_value = mock_response

            # Use parameters with special characters
            response = ofsc_instance.metadata.start_routing_plan(
                profile_label="Profile With Spaces",
                plan_label="Plan/Label",
                resource_external_id="RESOURCE@123",
                date="2025-10-23",
                response_type=FULL_RESPONSE
            )

            # Verify URL encoding was applied
            call_args = mock_post.call_args
            url = call_args[0][0]
            assert "Profile+With+Spaces" in url or "Profile%20With%20Spaces" in url
            assert "Plan%2FLabel" in url
            assert "RESOURCE%40123" in url


# Real API Tests (marked with uses_real_data)

@pytest.mark.uses_real_data
class TestRoutingProfileWriteRealAPI:
    """Real API tests for routing profile write operations

    These tests make actual API calls and are skipped by default.
    Run with: pytest -m uses_real_data
    """

    @pytest.fixture
    def sample_plan_data(self):
        """Load sample plan data from saved responses"""
        response_file = Path("tests/saved_responses/routing_profiles/export_routing_plan_actual_data.json")
        with open(response_file, "r") as f:
            data = json.load(f)
        return data["response_data"]

    def test_import_routing_plan_real_409(self, instance, sample_plan_data):
        """Test real API import returns 409 for existing plan"""
        plan_json = json.dumps(sample_plan_data)
        plan_bytes = plan_json.encode('utf-8')

        response = instance.metadata.import_routing_plan(
            profile_label="MaintenanceRoutingProfile",
            plan_data=plan_bytes,
            response_type=FULL_RESPONSE
        )

        # Should return 409 since Optimization plan already exists
        assert response.status_code == 409
        data = response.json()
        assert data["force"] == "required"

    def test_force_import_routing_plan_real_200(self, instance, sample_plan_data):
        """Test real API force import succeeds with 200"""
        plan_json = json.dumps(sample_plan_data)
        plan_bytes = plan_json.encode('utf-8')

        response = instance.metadata.force_import_routing_plan(
            profile_label="MaintenanceRoutingProfile",
            plan_data=plan_bytes,
            response_type=FULL_RESPONSE
        )

        # Should return 200 and successfully overwrite
        assert response.status_code == 200
        data = response.json()
        assert "successfully imported" in data["detail"]

    def test_import_export_roundtrip(self, instance):
        """Test exporting and re-importing a plan"""
        profile_label = "MaintenanceRoutingProfile"
        plan_label = "Optimization"

        # Step 1: Export the plan
        export_response = instance.metadata.export_routing_plan(
            profile_label=profile_label,
            plan_label=plan_label,
            response_type=FULL_RESPONSE
        )
        assert export_response.status_code == 200

        # The export should return JSON plan data
        plan_data = export_response.json()
        plan_bytes = json.dumps(plan_data).encode('utf-8')

        # Step 2: Force import it back (since it already exists)
        import_response = instance.metadata.force_import_routing_plan(
            profile_label=profile_label,
            plan_data=plan_bytes,
            response_type=FULL_RESPONSE
        )

        assert import_response.status_code == 200
        assert "successfully imported" in import_response.json()["detail"]

    def test_export_import_cycle_with_live_discovery(self, instance):
        """Test complete export->import cycle with live profile/plan discovery

        This test:
        1. Discovers the first available routing profile
        2. Gets the first plan in that profile
        3. Exports the plan using export_plan_file (returns raw bytes)
        4. Immediately force imports those bytes back to overwrite
        5. Verifies the complete cycle succeeds
        """
        # Step 1: Get routing profiles
        profiles = instance.metadata.get_routing_profiles()
        assert profiles.totalResults > 0, "No routing profiles available for testing"

        profile_label = profiles.items[0].profileLabel
        print(f"\nTesting with profile: {profile_label}")

        # Step 2: Get plans for first profile
        plans = instance.metadata.get_routing_profile_plans(profile_label=profile_label)
        assert plans.totalResults > 0, f"No plans in profile {profile_label}"

        plan_label = plans.items[0].planLabel
        print(f"Testing with plan: {plan_label}")

        # Step 3: Export plan as raw file (returns bytes ready for import)
        plan_bytes = instance.metadata.export_plan_file(
            profile_label=profile_label,
            plan_label=plan_label
        )

        # Verify we got bytes
        assert isinstance(plan_bytes, bytes), "export_plan_file should return bytes"
        assert len(plan_bytes) > 1000, f"Plan data too small ({len(plan_bytes)} bytes)"
        print(f"Exported {len(plan_bytes)} bytes")

        # Step 4: Force import the exported bytes back (overwrite)
        response = instance.metadata.force_import_routing_plan(
            profile_label=profile_label,
            plan_data=plan_bytes,
            response_type=FULL_RESPONSE
        )

        # Step 5: Verify success
        assert response.status_code == 200, f"Force import failed: {response.text}"
        data = response.json()
        assert "successfully imported" in data["detail"]
        print(f"✓ Complete export→import cycle succeeded for {profile_label}/{plan_label}")
