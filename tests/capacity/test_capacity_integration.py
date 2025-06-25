"""
Integration tests for capacity module functionality against real OFSC server.
Tests both getAvailableCapacity and getQuota functions.
These tests require valid OFSC credentials in .env file.
"""
import os
import pytest
from datetime import date, timedelta

from ofsc import OFSC
from ofsc.models import (
    CapacityRequest, GetCapacityResponse, 
    GetQuotaRequest, GetQuotaResponse, 
    QuotaAreaItem, CapacityAreaResponseItem,
    CsvList
)


@pytest.mark.integration
class TestCapacityModuleIntegration:
    """Integration tests for the entire capacity module"""
    
    @pytest.fixture(scope="class")
    def ofsc_instance(self):
        """Create OFSC instance with real credentials"""
        
        # Check for required environment variables
        required_vars = ["OFSC_CLIENT_ID", "OFSC_CLIENT_SECRET", "OFSC_COMPANY"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")
        
        return OFSC(
            clientID=os.environ.get("OFSC_CLIENT_ID"),
            secret=os.environ.get("OFSC_CLIENT_SECRET"), 
            companyName=os.environ.get("OFSC_COMPANY"),
            root=os.environ.get("OFSC_ROOT")
        )
    
    @pytest.fixture
    def test_dates(self):
        """Get today and tomorrow for testing"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return [today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")]
    
    @pytest.fixture
    def real_areas(self):
        """Real capacity areas for testing"""
        return ["FLUSA", "CAUSA"]
    
    @pytest.fixture
    def real_categories(self):
        """Real capacity categories for testing"""
        return ["EST", "RES", "COM"]
    
    def test_capacity_module_exists(self, ofsc_instance):
        """Test that capacity module is properly integrated"""
        
        # Verify capacity module exists
        assert hasattr(ofsc_instance, 'capacity')
        assert ofsc_instance.capacity is not None
        
        # Verify capacity functions exist
        assert hasattr(ofsc_instance.capacity, 'getAvailableCapacity')
        assert hasattr(ofsc_instance.capacity, 'getQuota')
        
        # Verify functions are callable
        assert callable(ofsc_instance.capacity.getAvailableCapacity)
        assert callable(ofsc_instance.capacity.getQuota)
    
    def test_available_capacity_basic(self, ofsc_instance, test_dates, real_areas):
        """Test basic getAvailableCapacity functionality"""
        
        # Make request with individual parameters
        response = ofsc_instance.capacity.getAvailableCapacity(
            dates=[test_dates[0]],
            areas=real_areas,
            availableTimeIntervals="all",
            calendarTimeIntervals="all"
        )
        
        # Verify response structure
        assert isinstance(response, GetCapacityResponse)
        assert len(response.items) == 1
        assert response.items[0].date == test_dates[0]
        assert len(response.items[0].areas) >= 1
        
        # Verify area structure
        area = response.items[0].areas[0]
        assert isinstance(area, CapacityAreaResponseItem)
        assert area.label is not None
        assert area.calendar is not None
        assert len(area.calendar.count) > 0
    
    def test_available_capacity_with_categories(self, ofsc_instance, test_dates, real_areas, real_categories):
        """Test getAvailableCapacity with categories"""
        
        response = ofsc_instance.capacity.getAvailableCapacity(
            dates=[test_dates[0]],
            areas=real_areas,
            categories=real_categories,
            availableTimeIntervals="all",
            calendarTimeIntervals="all"
        )
        
        # Verify response
        assert isinstance(response, GetCapacityResponse)
        assert len(response.items) == 1
        
        # Should have requested areas
        area_labels = [area.label for area in response.items[0].areas]
        for area_label in real_areas:
            assert area_label in area_labels
    
    def test_quota_vs_capacity_consistency(self, ofsc_instance, test_dates, real_areas):
        """Test that quota and capacity APIs return consistent area information"""
        
        # Get capacity data
        capacity_response = ofsc_instance.capacity.getAvailableCapacity(
            dates=[test_dates[0]],
            areas=real_areas
        )
        
        # Get quota data
        quota_response = ofsc_instance.capacity.getQuota(
            dates=[test_dates[0]],
            areas=real_areas
        )
        
        # Both should return data for the same areas
        capacity_areas = [area.label for area in capacity_response.items[0].areas]
        quota_areas = [area.label for area in quota_response.items[0].areas]
        
        # Check that requested areas are present in both responses
        for area_label in real_areas:
            # Area should be in at least one of the responses
            assert (area_label in capacity_areas or area_label in quota_areas)
    
    def test_capacity_different_intervals(self, ofsc_instance, test_dates, real_areas):
        """Test capacity with different time intervals"""
        
        # Test with different interval settings
        intervals_to_test = [
            ("all", "all"),
            ("15", "all"),
            ("all", "60")
        ]
        
        for available_interval, calendar_interval in intervals_to_test:
            response = ofsc_instance.capacity.getAvailableCapacity(
                dates=[test_dates[0]],
                areas=real_areas[:1],  # Use just one area for faster testing
                availableTimeIntervals=available_interval,
                calendarTimeIntervals=calendar_interval
            )
            
            # Should get valid response regardless of interval settings
            assert isinstance(response, GetCapacityResponse)
            assert len(response.items) == 1
    
    def test_capacity_multiple_dates(self, ofsc_instance, test_dates, real_areas):
        """Test capacity and quota with multiple dates"""
        
        # Test capacity
        capacity_response = ofsc_instance.capacity.getAvailableCapacity(
            dates=test_dates,
            areas=real_areas
        )
        
        # Test quota
        quota_response = ofsc_instance.capacity.getQuota(
            dates=test_dates,
            areas=real_areas
        )
        
        # Both should return data for both dates
        assert len(capacity_response.items) == len(test_dates)
        assert len(quota_response.items) == len(test_dates)
        
        # Verify dates match
        capacity_dates = [item.date for item in capacity_response.items]
        quota_dates = [item.date for item in quota_response.items]
        
        for test_date in test_dates:
            assert test_date in capacity_dates
            assert test_date in quota_dates
    
    def test_capacity_error_handling(self, ofsc_instance, test_dates):
        """Test error handling for invalid requests"""
        
        # Test capacity with invalid area
        try:
            response = ofsc_instance.capacity.getAvailableCapacity(
                dates=[test_dates[0]],
                areas=["INVALID_AREA_123"]
            )
            # If no exception, check response handles it gracefully
            assert isinstance(response, GetCapacityResponse)
        except Exception as e:
            # Should be a meaningful error
            assert "area" in str(e).lower() or "not found" in str(e).lower()
        
        # Test quota with invalid parameters
        try:
            response = ofsc_instance.capacity.getQuota(
                dates=[test_dates[0]],
                areas=["INVALID_AREA_456"]
            )
            assert isinstance(response, GetQuotaResponse)
        except Exception as e:
            assert "area" in str(e).lower() or "not found" in str(e).lower()
    
    def test_capacity_model_validation_edge_cases(self, ofsc_instance, test_dates, real_areas):
        """Test model validation with edge cases"""
        
        # Test capacity with empty categories
        response = ofsc_instance.capacity.getAvailableCapacity(
            dates=[test_dates[0]],
            areas=real_areas,
            categories=[]  # Empty categories
        )
        assert isinstance(response, GetCapacityResponse)
        
        # Test quota with None optional parameters (should use defaults)
        response = ofsc_instance.capacity.getQuota(
            dates=[test_dates[0]],
            areas=real_areas,
            categories=None,
            aggregateResults=None,
            categoryLevel=None
        )
        assert isinstance(response, GetQuotaResponse)


@pytest.mark.integration
@pytest.mark.slow
class TestCapacityPerformanceIntegration:
    """Performance and stress tests for capacity module"""
    
    @pytest.fixture(scope="class")
    def ofsc_instance(self):
        """Create OFSC instance with real credentials"""
        
        required_vars = ["OFSC_CLIENT_ID", "OFSC_CLIENT_SECRET", "OFSC_COMPANY"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")
        
        return OFSC(
            clientID=os.environ.get("OFSC_CLIENT_ID"),
            secret=os.environ.get("OFSC_CLIENT_SECRET"), 
            companyName=os.environ.get("OFSC_COMPANY"),
            root=os.environ.get("OFSC_ROOT")
        )
    
    def test_capacity_week_range_performance(self, ofsc_instance):
        """Test capacity API with week-long date range"""
        import time
        
        # Generate week range
        today = date.today()
        week_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        
        # Test capacity API
        start_time = time.time()
        capacity_response = ofsc_instance.capacity.getAvailableCapacity(
            dates=week_dates,
            areas=["FLUSA"]
        )
        capacity_time = time.time() - start_time
        
        # Test quota API
        start_time = time.time()
        quota_response = ofsc_instance.capacity.getQuota(
            dates=week_dates,
            areas=["FLUSA"]
        )
        quota_time = time.time() - start_time
        
        # Verify responses
        assert isinstance(capacity_response, GetCapacityResponse)
        assert isinstance(quota_response, GetQuotaResponse)
        assert len(capacity_response.items) == 7
        assert len(quota_response.items) == 7
        
        # Performance assertions (adjust thresholds as needed)
        assert capacity_time < 15.0  # Should complete within 15 seconds
        assert quota_time < 10.0     # Should complete within 10 seconds
        
        print(f"Capacity API (7 days): {capacity_time:.2f}s")
        print(f"Quota API (7 days): {quota_time:.2f}s")
    
    def test_concurrent_capacity_requests(self, ofsc_instance):
        """Test multiple concurrent capacity requests"""
        import concurrent.futures
        import time
        
        today = date.today()
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        def make_capacity_request(area):
            """Make a capacity request for a specific area"""
            return ofsc_instance.capacity.getAvailableCapacity(
                dates=[today_str],
                areas=[area]
            )
        
        def make_quota_request(area):
            """Make a quota request for a specific area"""
            return ofsc_instance.capacity.getQuota(
                dates=[today_str],
                areas=[area]
            )
        
        areas_to_test = ["FLUSA", "CAUSA"]
        
        # Test concurrent capacity requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            capacity_futures = [executor.submit(make_capacity_request, area) for area in areas_to_test]
            quota_futures = [executor.submit(make_quota_request, area) for area in areas_to_test]
            
            # Wait for all to complete
            capacity_results = [future.result() for future in capacity_futures]
            quota_results = [future.result() for future in quota_futures]
        
        concurrent_time = time.time() - start_time
        
        # Verify all requests succeeded
        for result in capacity_results:
            assert isinstance(result, GetCapacityResponse)
        for result in quota_results:
            assert isinstance(result, GetQuotaResponse)
        
        # Should complete reasonably quickly even with concurrent requests
        assert concurrent_time < 20.0
        
        print(f"Concurrent requests ({len(areas_to_test)} areas, both APIs): {concurrent_time:.2f}s")