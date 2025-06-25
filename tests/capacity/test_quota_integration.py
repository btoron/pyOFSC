"""
Integration tests for capacity quota functionality against real OFSC server.
These tests require valid OFSC credentials in .env file.
"""
import os
import pytest
from datetime import date, timedelta

from ofsc import OFSC
from ofsc.models import GetQuotaRequest, GetQuotaResponse, QuotaAreaItem, CsvList


@pytest.mark.integration
class TestQuotaAPIIntegration:
    """Integration tests against real OFSC server"""
    
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
    
    def test_quota_minimal_request(self, ofsc_instance, test_dates):
        """Test minimal quota request with only dates"""
        
        response = ofsc_instance.capacity.getQuota(dates=[test_dates[0]])
        
        # Verify response structure
        assert isinstance(response, GetQuotaResponse)
        assert len(response.items) == 1
        assert response.items[0].date == test_dates[0]
        assert len(response.items[0].areas) > 0
        
        # Verify area structure
        first_area = response.items[0].areas[0]
        assert isinstance(first_area, QuotaAreaItem)
        assert first_area.label is not None
        assert isinstance(first_area.maxAvailable, int)
    
    def test_quota_with_areas(self, ofsc_instance, test_dates, real_areas):
        """Test quota request with specific areas"""
        
        response = ofsc_instance.capacity.getQuota(
            dates=test_dates,
            areas=real_areas
        )
        
        # Verify response structure
        assert isinstance(response, GetQuotaResponse)
        assert len(response.items) == 2  # Two dates
        
        # Verify each date has the requested areas
        for item in response.items:
            assert item.date in test_dates
            assert len(item.areas) == len(real_areas)
            
            # Verify area labels match what was requested
            area_labels = [area.label for area in item.areas]
            for area_label in real_areas:
                assert area_label in area_labels
    
    def test_quota_with_categories(self, ofsc_instance, test_dates, real_areas, real_categories):
        """Test quota request with areas and categories"""
        
        response = ofsc_instance.capacity.getQuota(
            dates=[test_dates[0]],
            areas=real_areas,
            categories=real_categories
        )
        
        # Verify response structure
        assert isinstance(response, GetQuotaResponse)
        assert len(response.items) == 1
        
        # Should have areas matching the request
        area_labels = [area.label for area in response.items[0].areas]
        for area_label in real_areas:
            assert area_label in area_labels
    
    def test_quota_with_boolean_parameters(self, ofsc_instance, test_dates, real_areas):
        """Test quota request with boolean parameters"""
        
        response = ofsc_instance.capacity.getQuota(
            dates=[test_dates[0]],
            areas=real_areas,
            aggregateResults=True,
            categoryLevel=False,
            intervalLevel=True,
            returnStatuses=False,
            timeSlotLevel=True
        )
        
        # Verify response structure
        assert isinstance(response, GetQuotaResponse)
        assert len(response.items) == 1
        
        # With aggregateResults=True, we should get aggregated data
        # (may not have individual area labels)
        assert len(response.items[0].areas) >= 1
        
        # Verify aggregated area has expected fields
        area = response.items[0].areas[0]
        assert area.maxAvailable is not None
        assert area.used is not None
    
    def test_quota_different_input_formats(self, ofsc_instance, test_dates, real_areas):
        """Test different input formats produce same results"""
        
        # Test 1: List format
        response1 = ofsc_instance.capacity.getQuota(
            dates=test_dates[:1],
            areas=real_areas
        )
        
        # Test 2: CSV string format
        response2 = ofsc_instance.capacity.getQuota(
            dates=test_dates[0],
            areas=",".join(real_areas)
        )
        
        # Test 3: CsvList format
        response3 = ofsc_instance.capacity.getQuota(
            dates=CsvList.from_list(test_dates[:1]),
            areas=CsvList.from_list(real_areas)
        )
        
        # All responses should be equivalent
        assert len(response1.items) == len(response2.items) == len(response3.items)
        assert response1.items[0].date == response2.items[0].date == response3.items[0].date
        
        # Number of areas should match
        assert len(response1.items[0].areas) == len(response2.items[0].areas) == len(response3.items[0].areas)
    
    def test_quota_error_handling(self, ofsc_instance, test_dates):
        """Test error handling for invalid parameters"""
        
        # Test with invalid area (should not raise exception due to auto_model handling)
        try:
            response = ofsc_instance.capacity.getQuota(
                dates=test_dates[:1],
                areas=["INVALID_AREA_123"]
            )
            # If no exception, check if response is empty or handles gracefully
            assert isinstance(response, GetQuotaResponse)
        except Exception as e:
            # If exception is raised, it should be a meaningful error
            assert "area" in str(e).lower() or "not found" in str(e).lower()
    
    def test_quota_request_model_creation(self, test_dates, real_areas, real_categories):
        """Test GetQuotaRequest model creation and validation"""
        
        # Test full request
        request = GetQuotaRequest(
            dates=test_dates,
            areas=real_areas,
            categories=real_categories,
            aggregateResults=True,
            categoryLevel=False,
            intervalLevel=True,
            returnStatuses=False,
            timeSlotLevel=True
        )
        
        # Verify all fields are set correctly
        assert request.get_dates_list() == test_dates
        assert request.get_areas_list() == real_areas
        assert request.get_categories_list() == real_categories
        assert request.aggregateResults is True
        assert request.categoryLevel is False
        assert request.intervalLevel is True
        assert request.returnStatuses is False
        assert request.timeSlotLevel is True
        
        # Test minimal request (only dates required)
        minimal_request = GetQuotaRequest(dates=[test_dates[0]])
        assert minimal_request.get_dates_list() == [test_dates[0]]
        assert minimal_request.get_areas_list() == []
        assert minimal_request.get_categories_list() == []
        assert minimal_request.aggregateResults is None
    
    def test_quota_response_model_validation(self, ofsc_instance, test_dates, real_areas):
        """Test that response models validate correctly with real data"""
        
        response = ofsc_instance.capacity.getQuota(
            dates=[test_dates[0]],
            areas=real_areas
        )
        
        # Verify response model structure
        assert isinstance(response, GetQuotaResponse)
        assert hasattr(response, "items")
        assert len(response.items) > 0
        
        # Verify item structure
        item = response.items[0]
        assert hasattr(item, "date")
        assert hasattr(item, "areas")
        assert isinstance(item.date, str)
        assert isinstance(item.areas, list)
        
        # Verify area structure
        if item.areas:
            area = item.areas[0]
            assert isinstance(area, QuotaAreaItem)
            
            # Check that required fields are present
            assert hasattr(area, "maxAvailable")
            assert hasattr(area, "bookedActivities")
            assert hasattr(area, "used")
            
            # Verify field types
            if area.maxAvailable is not None:
                assert isinstance(area.maxAvailable, int)
            if area.bookedActivities is not None:
                assert isinstance(area.bookedActivities, int)
            if area.used is not None:
                assert isinstance(area.used, int)


@pytest.mark.integration
@pytest.mark.slow
class TestQuotaAPIPerformance:
    """Performance tests for quota API"""
    
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
    
    def test_quota_multiple_dates_performance(self, ofsc_instance):
        """Test performance with multiple dates"""
        import time
        
        # Generate date range (7 days)
        today = date.today()
        date_range = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        
        start_time = time.time()
        response = ofsc_instance.capacity.getQuota(
            dates=date_range,
            areas=["FLUSA", "CAUSA"]
        )
        end_time = time.time()
        
        # Verify response
        assert isinstance(response, GetQuotaResponse)
        assert len(response.items) == 7
        
        # Performance check (should complete in reasonable time)
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Should complete within 10 seconds
        
        print(f"Multiple dates query took {execution_time:.2f} seconds")
    
    def test_quota_large_area_set_performance(self, ofsc_instance):
        """Test performance with multiple areas (if available)"""
        import time
        
        today = date.today()
        
        # Try with multiple areas (adjust based on available areas)
        areas = ["FLUSA", "CAUSA"]  # Add more if available in your environment
        
        start_time = time.time()
        response = ofsc_instance.capacity.getQuota(
            dates=[today.strftime("%Y-%m-%d")],
            areas=areas
        )
        end_time = time.time()
        
        # Verify response
        assert isinstance(response, GetQuotaResponse)
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        
        print(f"Multiple areas query took {execution_time:.2f} seconds")