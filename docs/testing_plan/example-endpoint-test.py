# tests/integration/test_endpoints/test_activities.py
"""
Example implementation of activity endpoint tests.
This demonstrates the complete testing pattern for a single endpoint.
"""
import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tests.utils.base_test import APITestBase
from tests.utils.parameter_testing import (
    ParameterTestCase, EndpointTestSuite, TestCategory,
    ParameterGenerator, generate_pairwise_combinations
)

# Import your models here
# from oracle_field_service_proxy.models.requests import CreateActivityRequest, UpdateActivityRequest
# from oracle_field_service_proxy.models.responses import ActivityResponse, ActivityListResponse
# from oracle_field_service_proxy.exceptions import OFSValidationError, OFSNotFoundError

class TestActivitiesEndpoint(APITestBase):
    """Complete test suite for activities endpoint"""
    
    ENDPOINT_NAME = "activities"
    CLEANUP_ORDER = ["activities"]  # Clean up activities before other resources
    
    # Define test data for this endpoint
    @pytest.fixture(scope="class")
    def activity_test_suite(self) -> EndpointTestSuite:
        """Define all test cases for activities endpoint"""
        
        test_cases = []
        
        # Happy path tests
        test_cases.extend([
            ParameterTestCase(
                test_id="create_basic_activity",
                description="Create activity with minimum required fields",
                category=TestCategory.HAPPY_PATH,
                parameters={
                    "name": "Basic Service Call",
                    "activityType": "service",
                    "duration": 60,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "timeSlot": "all-day"
                },
                expected_response={
                    "status": "pending"
                },
                tags=["smoke", "create"]
            ),
            ParameterTestCase(
                test_id="create_detailed_activity",
                description="Create activity with all optional fields",
                category=TestCategory.HAPPY_PATH,
                parameters={
                    "name": "Detailed Installation",
                    "activityType": "install",
                    "duration": 120,
                    "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "timeSlot": "AM",
                    "customer": {
                        "name": "Test Customer",
                        "phone": "+1234567890",
                        "email": "test@example.com"
                    },
                    "address": {
                        "street": "123 Test St",
                        "city": "Test City",
                        "state": "TS",
                        "postalCode": "12345"
                    },
                    "skills": ["electrical", "plumbing"],
                    "priority": "high",
                    "notes": "Important installation"
                },
                tags=["detailed", "create"]
            )
        ])
        
        # Boundary tests - String fields
        for test_id, value, should_pass in ParameterGenerator.generate_string_boundaries("name"):
            params = {
                "name": value,
                "activityType": "service",
                "duration": 60,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            test_cases.append(ParameterTestCase(
                test_id=f"boundary_{test_id}",
                description=f"Test name field boundary: {test_id}",
                category=TestCategory.BOUNDARY,
                parameters=params,
                expected_status=200 if should_pass else 400,
                expected_error=None if should_pass else "Invalid name",
                should_cleanup=should_pass,
                tags=["boundary", "name"]
            ))
        
        # Boundary tests - Numeric fields
        for test_id, value, should_pass in ParameterGenerator.generate_numeric_boundaries(
            "duration", min_value=1, max_value=1440
        ):
            params = {
                "name": f"Duration Test {test_id}",
                "activityType": "service",
                "duration": value,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            test_cases.append(ParameterTestCase(
                test_id=f"boundary_{test_id}",
                description=f"Test duration field boundary: {test_id}",
                category=TestCategory.BOUNDARY,
                parameters=params,
                expected_status=200 if should_pass else 400,
                expected_error=None if should_pass else "Invalid duration",
                should_cleanup=should_pass,
                tags=["boundary", "duration"]
            ))
        
        # Negative tests
        test_cases.extend([
            ParameterTestCase(
                test_id="missing_required_name",
                description="Missing required field: name",
                category=TestCategory.NEGATIVE,
                parameters={
                    "activityType": "service",
                    "duration": 60
                },
                expected_status=400,
                expected_error="name is required",
                should_cleanup=False,
                tags=["negative", "validation"]
            ),
            ParameterTestCase(
                test_id="invalid_activity_type",
                description="Invalid enum value for activityType",
                category=TestCategory.NEGATIVE,
                parameters={
                    "name": "Invalid Type Test",
                    "activityType": "invalid_type",
                    "duration": 60
                },
                expected_status=400,
                expected_error="Invalid activity type",
                should_cleanup=False,
                tags=["negative", "validation"]
            ),
            ParameterTestCase(
                test_id="invalid_date_format",
                description="Invalid date format",
                category=TestCategory.NEGATIVE,
                parameters={
                    "name": "Date Format Test",
                    "activityType": "service",
                    "duration": 60,
                    "date": "2024/01/01"  # Wrong format
                },
                expected_status=400,
                expected_error="Invalid date format",
                should_cleanup=False,
                tags=["negative", "date"]
            )
        ])
        
        # Edge cases
        test_cases.extend([
            ParameterTestCase(
                test_id="unicode_in_name",
                description="Unicode characters in name",
                category=TestCategory.EDGE_CASE,
                parameters={
                    "name": "Service Call 测试 🚀",
                    "activityType": "service",
                    "duration": 60
                },
                tags=["edge", "unicode"]
            ),
            ParameterTestCase(
                test_id="max_skills_array",
                description="Maximum number of skills",
                category=TestCategory.EDGE_CASE,
                parameters={
                    "name": "Multi-skill Activity",
                    "activityType": "service",
                    "duration": 60,
                    "skills": [f"skill_{i}" for i in range(50)]  # Max allowed
                },
                tags=["edge", "array"]
            )
        ])
        
        return EndpointTestSuite(
            endpoint_name="activities",
            method="POST",
            path_template="/activities",
            test_cases=test_cases,
            rate_limit=10
        )
    
    @pytest.mark.integration
    @pytest.mark.parametrize("test_case", 
                           lambda: activity_test_suite.test_cases,
                           ids=lambda tc: tc.test_id)
    async def test_create_activity_comprehensive(self, 
                                               client, 
                                               test_case: ParameterTestCase,
                                               created_resources,
                                               auto_cleanup,
                                               error_reporter,
                                               rate_limiter):
        """Comprehensive parameter testing for activity creation"""
        
        # Skip if needed
        if test_case.skip_reason:
            pytest.skip(test_case.skip_reason)
        
        # Apply rate limiting
        async with rate_limiter(self.ENDPOINT_NAME):
            
            if test_case.expected_status == 200:
                # Expected to succeed
                try:
                    # Create request model
                    request = CreateActivityRequest(**test_case.parameters)
                    
                    # Make API call
                    response = await client.create_activity(request)
                    
                    # Validate response
                    await self.assert_response_model(response, ActivityResponse)
                    
                    # Check expected response fields
                    if test_case.expected_response:
                        for field, expected_value in test_case.expected_response.items():
                            assert getattr(response, field) == expected_value, \
                                f"Expected {field}={expected_value}, got {getattr(response, field)}"
                    
                    # Track for cleanup
                    if test_case.should_cleanup:
                        created_resources.append({
                            "type": "activity",
                            "id": response.id,
                            "client": client
                        })
                    
                    print(f"✓ {test_case.test_id}: Created activity {response.id}")
                    
                except Exception as e:
                    error_reporter(e, {
                        "test_case": test_case.test_id,
                        "parameters": test_case.parameters
                    })
                    pytest.fail(f"Test {test_case.test_id} unexpectedly failed: {e}")
            
            else:
                # Expected to fail
                with pytest.raises(OFSValidationError) as exc_info:
                    request = CreateActivityRequest(**test_case.parameters)
                    await client.create_activity(request)
                
                # Validate error
                await self.assert_error_response(
                    exc_info.value,
                    test_case.expected_status,
                    test_case.expected_error
                )
                
                print(f"✓ {test_case.test_id}: Correctly rejected with: {exc_info.value}")
    
    @pytest.mark.integration
    async def test_activity_crud_operations(self, client, created_resources, auto_cleanup):
        """Test complete CRUD operations for activities"""
        
        # CREATE
        create_request = CreateActivityRequest(
            name="CRUD Test Activity",
            activityType="service",
            duration=90,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        created_activity = await client.create_activity(create_request)
        created_resources.append({
            "type": "activity",
            "id": created_activity.id,
            "client": client
        })
        
        # READ
        read_activity = await client.get_activity(created_activity.id)
        assert read_activity.id == created_activity.id
        assert read_activity.name == create_request.name
        
        # UPDATE
        update_request = UpdateActivityRequest(
            duration=120,
            notes="Updated via API test"
        )
        
        updated_activity = await client.update_activity(
            created_activity.id, 
            update_request
        )
        assert updated_activity.duration == 120
        assert updated_activity.notes == "Updated via API test"
        
        # DELETE
        await client.delete_activity(created_activity.id)
        
        # Verify deletion
        with pytest.raises(OFSNotFoundError):
            await client.get_activity(created_activity.id)
        
        # Remove from cleanup list since we deleted it
        created_resources.pop()
    
    @pytest.mark.integration
    async def test_activity_search_filters(self, client, test_data_ids):
        """Test activity search with various filters"""
        
        test_filters = [
            # Single filters
            {"activityType": "service"},
            {"date": datetime.now().strftime("%Y-%m-%d")},
            {"status": "pending"},
            
            # Date range
            {
                "dateFrom": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "dateTo": datetime.now().strftime("%Y-%m-%d")
            },
            
            # Pagination
            {"limit": 10, "offset": 0},
            {"limit": 5, "offset": 10},
            
            # Sorting
            {"sortBy": "date", "sortOrder": "asc"},
            {"sortBy": "priority", "sortOrder": "desc"},
            
            # Combined filters
            {
                "activityType": "service",
                "status": "pending",
                "limit": 20,
                "sortBy": "date",
                "sortOrder": "desc"
            }
        ]
        
        for filters in test_filters:
            response = await client.search_activities(**filters)
            
            await self.assert_response_model(response, ActivityListResponse)
            
            # Validate filter application
            if "activityType" in filters:
                for activity in response.items:
                    assert activity.activityType == filters["activityType"]
            
            if "limit" in filters:
                assert len(response.items) <= filters["limit"]
            
            print(f"✓ Search with filters {filters}: {len(response.items)} results")
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_activity_pagination_complete(self, client):
        """Test complete pagination through all activities"""
        
        all_activities = []
        page_size = 50
        offset = 0
        
        while True:
            response = await client.search_activities(
                limit=page_size,
                offset=offset,
                sortBy="id",
                sortOrder="asc"
            )
            
            all_activities.extend(response.items)
            
            if len(response.items) < page_size:
                break
            
            offset += page_size
            
            # Prevent infinite loops
            if offset > 10000:
                pytest.fail("Too many activities, stopping pagination test")
        
        print(f"✓ Retrieved {len(all_activities)} total activities via pagination")
        
        # Verify no duplicates
        activity_ids = [a.id for a in all_activities]
        assert len(activity_ids) == len(set(activity_ids)), "Duplicate activities in pagination"
    
    @pytest.mark.integration
    async def test_activity_concurrent_operations(self, client, rate_limiter):
        """Test concurrent operations respect rate limits"""
        
        async def create_activity(index: int):
            async with rate_limiter(self.ENDPOINT_NAME):
                request = CreateActivityRequest(
                    name=f"Concurrent Test {index}",
                    activityType="service",
                    duration=30
                )
                return await client.create_activity(request)
        
        # Create 20 activities concurrently (but rate limited to 10)
        tasks = [create_activity(i) for i in range(20)]
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (datetime.now() - start_time).total_seconds()
        
        # Should take at least 2 batches due to rate limit
        assert duration > 1.0, "Concurrent operations too fast, rate limiting may not be working"
        
        # Check results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        print(f"✓ Concurrent operations: {len(successful)} succeeded, {len(failed)} failed")
        
        # Cleanup
        for result in successful:
            if hasattr(result, 'id'):
                await client.delete_activity(result.id)