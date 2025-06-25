"""
Mocked tests for capacity functionality using mock responses.
Tests both getAvailableCapacity and getQuota functions.
"""
import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from ofsc import OFSC
from ofsc.models import (
    CapacityRequest, GetCapacityResponse, 
    GetQuotaRequest, GetQuotaResponse, 
    QuotaAreaItem, CsvList
)
from ofsc.capacity import _convert_model_to_api_params


class TestCapacityAPIMocked:
    """Test the capacity API with mocked responses"""
    
    @pytest.fixture
    def ofsc_instance(self):
        """Create OFSC instance for testing"""
        return OFSC(
            clientID="test_client",
            secret="test_secret", 
            companyName="test_company"
        )
    
    @pytest.fixture
    def mock_capacity_response(self):
        """Mock capacity response data"""
        return {
            "items": [
                {
                    "date": "2025-06-25",
                    "areas": [
                        {
                            "label": "FLUSA",
                            "name": "FL, USA",
                            "calendar": {
                                "count": [480, 480, 480],
                                "minutes": [28800, 28800, 28800]
                            },
                            "available": {
                                "count": [120, 150, 100],
                                "minutes": [7200, 9000, 6000]
                            },
                            "categories": []
                        }
                    ]
                }
            ]
        }
    
    def test_available_capacity_request(self, ofsc_instance, mock_capacity_response):
        """Test getAvailableCapacity function with new individual parameter signature"""
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_capacity_response
            mock_get.return_value = mock_response
            
            # Make the call with individual parameters
            result = ofsc_instance.capacity.getAvailableCapacity(
                dates=["2025-06-25"],
                areas=["FLUSA", "CAUSA"],
                availableTimeIntervals="all",
                calendarTimeIntervals="all"
            )
            
            # Verify it's the correct type
            assert isinstance(result, GetCapacityResponse)
            
            # Verify structure
            assert len(result.items) == 1
            assert result.items[0].date == "2025-06-25"
            assert len(result.items[0].areas) == 1
            
            # Verify area data
            area = result.items[0].areas[0]
            assert area.label == "FLUSA"
            assert area.name == "FL, USA"
            assert area.calendar.count == [480, 480, 480]
            assert area.available.count == [120, 150, 100]
            
            # Verify the request was made to correct endpoint
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "/rest/ofscCapacity/v1/capacity" in call_args[0][0]
            
            # Verify parameters were converted correctly
            params = call_args[1]["params"]
            assert params["areas"] == "FLUSA,CAUSA"
            assert params["dates"] == "2025-06-25"
    
    def test_available_capacity_different_input_formats(self, ofsc_instance):
        """Test getAvailableCapacity with different input formats"""
        
        mock_response_data = {"items": [{"date": "2025-06-25", "areas": []}]}
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test 1: List input
            ofsc_instance.capacity.getAvailableCapacity(
                dates=["2025-06-25"],
                areas=["FLUSA", "CAUSA"]
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
            assert call_args[1]["params"]["dates"] == "2025-06-25"
            
            # Test 2: CSV string input
            mock_get.reset_mock()
            ofsc_instance.capacity.getAvailableCapacity(
                dates="2025-06-25",
                areas="FLUSA,CAUSA",
                categories="EST,RES"
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
            assert call_args[1]["params"]["categories"] == "EST,RES"
            
            # Test 3: CsvList input
            mock_get.reset_mock()
            ofsc_instance.capacity.getAvailableCapacity(
                dates=CsvList.from_list(["2025-06-25"]),
                areas=CsvList.from_list(["FLUSA", "CAUSA"])
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
    
    def test_available_capacity_with_optional_parameters(self, ofsc_instance):
        """Test getAvailableCapacity with optional parameters"""
        
        mock_response_data = {"items": []}
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test with all parameters
            ofsc_instance.capacity.getAvailableCapacity(
                dates=["2025-06-25"],
                areas=["FLUSA"],
                categories=["EST"],
                aggregateResults=True,
                availableTimeIntervals="15",
                calendarTimeIntervals="60",
                fields=["label", "name"]
            )
            
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            
            assert params["aggregateResults"] == "true"  # Should be converted to lowercase
            assert params["availableTimeIntervals"] == "15"
            assert params["calendarTimeIntervals"] == "60"
            assert params["fields"] == ["label", "name"]


class TestQuotaRequestValidation:
    """Test GetQuotaRequest model validation and conversion"""
    
    def test_quota_request_with_lists(self):
        """Test GetQuotaRequest with list inputs (should work with validators)"""
        
        # This should work because of the field validators
        request = GetQuotaRequest(
            dates=["2025-06-25", "2025-06-26"],
            areas=["FLUSA", "CAUSA"],
            categories=["EST", "RES"]
        )
        
        assert isinstance(request.dates, CsvList)
        assert isinstance(request.areas, CsvList)
        assert isinstance(request.categories, CsvList)
        
        # Test conversion back to lists
        assert request.get_dates_list() == ["2025-06-25", "2025-06-26"]
        assert request.get_areas_list() == ["FLUSA", "CAUSA"]
        assert request.get_categories_list() == ["EST", "RES"]
    
    def test_quota_request_with_csv_strings(self):
        """Test GetQuotaRequest with CSV string inputs"""
        
        request = GetQuotaRequest(
            dates="2025-06-25,2025-06-26",
            areas="FLUSA,CAUSA",
            categories="EST,RES"
        )
        
        assert request.get_dates_list() == ["2025-06-25", "2025-06-26"]
        assert request.get_areas_list() == ["FLUSA", "CAUSA"]
        assert request.get_categories_list() == ["EST", "RES"]
    
    def test_quota_request_with_csvlist_objects(self):
        """Test GetQuotaRequest with CsvList inputs"""
        
        request = GetQuotaRequest(
            dates=CsvList.from_list(["2025-06-25"]),
            areas=CsvList.from_list(["FLUSA"]),
            categories=CsvList.from_list(["EST"])
        )
        
        assert request.get_dates_list() == ["2025-06-25"]
        assert request.get_areas_list() == ["FLUSA"]
        assert request.get_categories_list() == ["EST"]
    
    def test_quota_request_optional_fields(self):
        """Test GetQuotaRequest with optional fields"""
        
        # Minimal request (only dates required)
        minimal_request = GetQuotaRequest(dates=["2025-06-25"])
        
        assert minimal_request.get_dates_list() == ["2025-06-25"]
        assert minimal_request.get_areas_list() == []
        assert minimal_request.get_categories_list() == []
        assert minimal_request.aggregateResults is None
        assert minimal_request.categoryLevel is None
        
        # Request with boolean fields
        bool_request = GetQuotaRequest(
            dates=["2025-06-25"],
            aggregateResults=True,
            categoryLevel=False,
            intervalLevel=True
        )
        
        assert bool_request.aggregateResults is True
        assert bool_request.categoryLevel is False
        assert bool_request.intervalLevel is True
        assert bool_request.returnStatuses is None
        assert bool_request.timeSlotLevel is None


class TestQuotaResponseModel:
    """Test QuotaAreaItem and related models"""
    
    def test_quota_area_item_creation(self):
        """Test QuotaAreaItem model creation with various field combinations"""
        
        # Full area data
        full_area = QuotaAreaItem(
            label="FLUSA",
            name="FL, USA",
            maxAvailable=14158,
            otherActivities=971,
            quota=None,
            quotaPercent=None,
            minQuota=0,
            used=11888,
            usedQuotaPercent=None,
            bookedActivities=237
        )
        
        assert full_area.label == "FLUSA"
        assert full_area.name == "FL, USA"
        assert full_area.maxAvailable == 14158
        assert full_area.bookedActivities == 237
        
        # Area with quota set
        quota_area = QuotaAreaItem(
            label="South Florida",
            name="South Florida", 
            maxAvailable=9454,
            quota=0,
            quotaPercent=0,
            usedQuotaPercent=0,
            bookedActivities=143
        )
        
        assert quota_area.quota == 0
        assert quota_area.quotaPercent == 0
        assert quota_area.usedQuotaPercent == 0
        
        # Aggregated area (no label)
        aggregated_area = QuotaAreaItem(
            maxAvailable=19666,
            used=16598,
            bookedActivities=329
        )
        
        assert aggregated_area.label is None
        assert aggregated_area.maxAvailable == 19666
        assert aggregated_area.used == 16598


class TestCsvListModel:
    """Test CsvList utility model"""
    
    def test_csvlist_from_list(self):
        """Test CsvList creation from list"""
        
        # Normal list
        csv_list = CsvList.from_list(["FLUSA", "CAUSA", "EST"])
        assert csv_list.value == "FLUSA,CAUSA,EST"
        assert csv_list.to_list() == ["FLUSA", "CAUSA", "EST"]
        
        # Empty list
        empty_csv = CsvList.from_list([])
        assert empty_csv.value == ""
        assert empty_csv.to_list() == []
        
        # Single item
        single_csv = CsvList.from_list(["FLUSA"])
        assert single_csv.value == "FLUSA"
        assert single_csv.to_list() == ["FLUSA"]
    
    def test_csvlist_to_list(self):
        """Test CsvList conversion to list"""
        
        # Normal CSV
        csv_list = CsvList(value="FLUSA,CAUSA,EST")
        assert csv_list.to_list() == ["FLUSA", "CAUSA", "EST"]
        
        # CSV with spaces
        spaced_csv = CsvList(value="FLUSA, CAUSA , EST ")
        assert spaced_csv.to_list() == ["FLUSA", "CAUSA", "EST"]
        
        # Empty string
        empty_csv = CsvList(value="")
        assert empty_csv.to_list() == []
        
        # Whitespace only
        whitespace_csv = CsvList(value="   ")
        assert whitespace_csv.to_list() == []
    
    def test_csvlist_string_methods(self):
        """Test CsvList string representation methods"""
        
        csv_list = CsvList.from_list(["FLUSA", "CAUSA"])
        
        # String representation should return CSV value
        assert str(csv_list) == "FLUSA,CAUSA"
        
        # Repr should show both formats
        repr_str = repr(csv_list)
        assert "CsvList(value='FLUSA,CAUSA'" in repr_str
        assert "list=['FLUSA', 'CAUSA']" in repr_str


class TestCapacityRequestModel:
    """Test CapacityRequest model with CsvList support"""
    
    def test_capacity_request_with_lists(self):
        """Test CapacityRequest model creation with list inputs"""
        
        request = CapacityRequest(
            areas=["FLUSA", "CAUSA"],
            dates=["2025-06-25", "2025-06-26"],
            availableTimeIntervals="all",
            calendarTimeIntervals="all",
            categories=["EST", "RES"],
            aggregateResults=True
        )
        
        assert isinstance(request.areas, CsvList)
        assert isinstance(request.dates, CsvList)
        assert isinstance(request.categories, CsvList)
        assert request.get_areas_list() == ["FLUSA", "CAUSA"]
        assert request.get_dates_list() == ["2025-06-25", "2025-06-26"]
        assert request.get_categories_list() == ["EST", "RES"]
        assert request.availableTimeIntervals == "all"
        assert request.calendarTimeIntervals == "all"
        assert request.aggregateResults is True
    
    def test_capacity_request_with_csv_strings(self):
        """Test CapacityRequest with CSV string inputs"""
        
        request = CapacityRequest(
            areas="FLUSA,CAUSA",
            dates="2025-06-25,2025-06-26",
            categories="EST,RES"
        )
        
        assert request.get_areas_list() == ["FLUSA", "CAUSA"]
        assert request.get_dates_list() == ["2025-06-25", "2025-06-26"]
        assert request.get_categories_list() == ["EST", "RES"]
    
    def test_capacity_request_with_csvlist_objects(self):
        """Test CapacityRequest with CsvList inputs"""
        
        request = CapacityRequest(
            areas=CsvList.from_list(["FLUSA"]),
            dates=CsvList.from_list(["2025-06-25"]),
            categories=CsvList.from_list(["EST"])
        )
        
        assert request.get_areas_list() == ["FLUSA"]
        assert request.get_dates_list() == ["2025-06-25"]
        assert request.get_categories_list() == ["EST"]
    
    def test_capacity_request_defaults(self):
        """Test CapacityRequest model with default values"""
        
        # Minimal request
        request = CapacityRequest(
            areas=["FLUSA"],
            dates=["2025-06-25"]
        )
        
        # Check defaults
        assert request.availableTimeIntervals == "all"
        assert request.calendarTimeIntervals == "all"
        assert request.get_categories_list() == []  # None categories should return empty list
        assert request.aggregateResults is None
        assert request.fields is None


class TestGenericConverter:
    """Test the internal _convert_model_to_api_params function"""
    
    def test_capacity_request_conversion(self):
        """Test conversion of CapacityRequest with various field types"""
        
        request = CapacityRequest(
            dates=["2025-06-25", "2025-06-26"],
            areas=["FLUSA", "CAUSA"],
            categories=["EST", "RES"],
            aggregateResults=True,
            availableTimeIntervals="15",
            calendarTimeIntervals="all"
        )
        
        params = _convert_model_to_api_params(request)
        
        # Verify CsvList fields are converted to strings
        assert params['dates'] == "2025-06-25,2025-06-26"
        assert params['areas'] == "FLUSA,CAUSA"
        assert params['categories'] == "EST,RES"
        
        # Verify boolean field is converted to lowercase string
        assert params['aggregateResults'] == "true"
        
        # Verify string fields remain unchanged
        assert params['availableTimeIntervals'] == "15"
        assert params['calendarTimeIntervals'] == "all"
    
    def test_quota_request_conversion(self):
        """Test conversion of GetQuotaRequest with boolean fields"""
        
        request = GetQuotaRequest(
            dates=["2025-06-25"],
            areas=["FLUSA"],
            aggregateResults=True,
            categoryLevel=False,
            intervalLevel=True,
            returnStatuses=False,
            timeSlotLevel=True
        )
        
        params = _convert_model_to_api_params(request)
        
        # Verify CsvList fields
        assert params['dates'] == "2025-06-25"
        assert params['areas'] == "FLUSA"
        
        # Verify all boolean fields are converted to lowercase strings
        assert params['aggregateResults'] == "true"
        assert params['categoryLevel'] == "false"
        assert params['intervalLevel'] == "true"
        assert params['returnStatuses'] == "false"
        assert params['timeSlotLevel'] == "true"
    
    def test_optional_field_exclusion(self):
        """Test that None optional fields are excluded"""
        
        request = CapacityRequest(
            dates=["2025-06-25"],
            areas=["FLUSA"]
            # categories omitted (None)
        )
        
        params = _convert_model_to_api_params(request)
        
        # Required fields should be present
        assert 'dates' in params
        assert 'areas' in params
        
        # None optional fields should be excluded
        assert 'categories' not in params
        
        # Default values should be included
        assert params['availableTimeIntervals'] == "all"
        assert params['calendarTimeIntervals'] == "all"
    
    def test_different_input_formats(self):
        """Test conversion with different input formats"""
        
        # CSV string inputs
        request1 = CapacityRequest(
            dates="2025-06-25,2025-06-26",
            areas="FLUSA,CAUSA"
        )
        
        params1 = _convert_model_to_api_params(request1)
        assert params1['dates'] == "2025-06-25,2025-06-26"
        assert params1['areas'] == "FLUSA,CAUSA"
        
        # CsvList inputs
        request2 = CapacityRequest(
            dates=CsvList.from_list(["2025-06-25"]),
            areas=CsvList.from_list(["FLUSA"])
        )
        
        params2 = _convert_model_to_api_params(request2)
        assert params2['dates'] == "2025-06-25"
        assert params2['areas'] == "FLUSA"
    
    def test_type_inspection_accuracy(self):
        """Test that type inspection correctly identifies field types"""
        
        # Create a request with mixed field types
        request = GetQuotaRequest(
            dates=["2025-06-25"],  # CsvList field
            aggregateResults=True,  # Optional[bool] field
            categoryLevel=False,    # Optional[bool] field
        )
        
        params = _convert_model_to_api_params(request)
        
        # Verify type inspection worked correctly
        assert isinstance(params['dates'], str)  # CsvList -> str
        assert isinstance(params['aggregateResults'], str)  # bool -> str
        assert isinstance(params['categoryLevel'], str)  # bool -> str
        
        # Verify actual conversions
        assert params['dates'] == "2025-06-25"
        assert params['aggregateResults'] == "true"
        assert params['categoryLevel'] == "false"