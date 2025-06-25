"""
Mocked tests for capacity quota functionality using real server response data.
These tests use captured real responses to ensure consistent testing without server dependency.
"""
import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from ofsc import OFSC
from ofsc.models import GetQuotaRequest, GetQuotaResponse, QuotaAreaItem, QuotaResponseItem, CsvList


class TestQuotaAPIMocked:
    """Test the quota API with mocked responses based on real server data"""
    
    @pytest.fixture
    def real_responses(self):
        """Load real server responses from captured JSON"""
        responses_file = Path(__file__).parent / "real_responses.json"
        with open(responses_file, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def ofsc_instance(self):
        """Create OFSC instance for testing"""
        return OFSC(
            clientID="test_client",
            secret="test_secret", 
            companyName="test_company"
        )
    
    def test_quota_minimal_dates_only(self, ofsc_instance, real_responses):
        """Test quota request with only dates (minimal case)"""
        
        # Get real response data
        scenario_data = real_responses["minimal_dates_only"]
        mock_response_data = scenario_data["response_data"]
        
        # Mock the requests.get call
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Make the call
            result = ofsc_instance.capacity.getQuota(dates=["2025-06-25"])
            
            # Verify it's the correct type
            assert isinstance(result, GetQuotaResponse)
            
            # Verify structure
            assert len(result.items) == 1
            assert result.items[0].date == "2025-06-25"
            assert len(result.items[0].areas) == 4
            
            # Verify specific area data
            flusa_area = next((area for area in result.items[0].areas if area.label == "FLUSA"), None)
            assert flusa_area is not None
            assert flusa_area.name == "FL, USA"
            assert flusa_area.maxAvailable == 14158
            assert flusa_area.bookedActivities == 237
            assert flusa_area.used == 11888
            
            # Verify the request was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "/rest/ofscCapacity/v2/quota" in call_args[0][0]
            assert call_args[1]["params"]["dates"] == "2025-06-25"
    
    def test_quota_with_areas(self, ofsc_instance, real_responses):
        """Test quota request with specific areas"""
        
        scenario_data = real_responses["with_areas"]
        mock_response_data = scenario_data["response_data"]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test with list of areas
            result = ofsc_instance.capacity.getQuota(
                dates=["2025-06-25", "2025-06-26"],
                areas=["FLUSA", "CAUSA"]
            )
            
            # Verify structure
            assert isinstance(result, GetQuotaResponse)
            assert len(result.items) == 2
            
            # Verify first date
            first_item = result.items[0]
            assert first_item.date == "2025-06-25"
            assert len(first_item.areas) == 2
            
            # Verify FLUSA and CAUSA are present
            area_labels = [area.label for area in first_item.areas]
            assert "FLUSA" in area_labels
            assert "CAUSA" in area_labels
            
            # Verify second date
            second_item = result.items[1]
            assert second_item.date == "2025-06-26"
            assert len(second_item.areas) == 2
            
            # Verify request parameters
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
            assert call_args[1]["params"]["dates"] == "2025-06-25,2025-06-26"
    
    def test_quota_with_categories(self, ofsc_instance, real_responses):
        """Test quota request with categories"""
        
        scenario_data = real_responses["with_categories"]
        mock_response_data = scenario_data["response_data"]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test with categories
            result = ofsc_instance.capacity.getQuota(
                dates=["2025-06-25"],
                areas=["FLUSA"],
                categories=["EST", "RES", "COM"]
            )
            
            # Verify structure
            assert isinstance(result, GetQuotaResponse)
            assert len(result.items) == 1
            assert len(result.items[0].areas) == 1
            
            # Verify area data
            area = result.items[0].areas[0]
            assert area.label == "FLUSA"
            assert area.name == "FL, USA"
            
            # Verify request parameters included categories
            call_args = mock_get.call_args
            assert call_args[1]["params"]["categories"] == "EST,RES,COM"
    
    def test_quota_with_boolean_parameters(self, ofsc_instance, real_responses):
        """Test quota request with boolean parameters"""
        
        scenario_data = real_responses["with_boolean_flags"]
        mock_response_data = scenario_data["response_data"]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test with boolean flags
            result = ofsc_instance.capacity.getQuota(
                dates=["2025-06-25"],
                areas=["FLUSA", "CAUSA"],
                aggregateResults=True,
                categoryLevel=False,
                intervalLevel=True,
                returnStatuses=False,
                timeSlotLevel=True
            )
            
            # Verify structure
            assert isinstance(result, GetQuotaResponse)
            assert len(result.items) == 1
            assert len(result.items[0].areas) == 1
            
            # Verify aggregated area data (no label when aggregated)
            area = result.items[0].areas[0]
            assert area.label is None  # Aggregated results don't have labels
            assert area.maxAvailable == 19666
            assert area.used == 16598
            assert area.bookedActivities == 329
            
            # Verify boolean parameters were converted to lowercase strings
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["aggregateResults"] == "true"
            assert params["categoryLevel"] == "false"
            assert params["intervalLevel"] == "true"
            assert params["returnStatuses"] == "false"
            assert params["timeSlotLevel"] == "true"
    
    def test_quota_request_model_validation(self):
        """Test GetQuotaRequest model validation and conversion"""
        
        # Test with list[str] - should convert to CsvList
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
        
        # Test with CSV strings
        request2 = GetQuotaRequest(
            dates="2025-06-25,2025-06-26",
            areas="FLUSA,CAUSA",
            categories="EST,RES"
        )
        
        assert request2.get_dates_list() == ["2025-06-25", "2025-06-26"]
        assert request2.get_areas_list() == ["FLUSA", "CAUSA"]
        assert request2.get_categories_list() == ["EST", "RES"]
        
        # Test with CsvList objects
        request3 = GetQuotaRequest(
            dates=CsvList.from_list(["2025-06-25"]),
            areas=CsvList.from_list(["FLUSA"]),
            categories=CsvList.from_list(["EST"])
        )
        
        assert request3.get_dates_list() == ["2025-06-25"]
        assert request3.get_areas_list() == ["FLUSA"]
        assert request3.get_categories_list() == ["EST"]
    
    def test_quota_area_item_model(self, real_responses):
        """Test QuotaAreaItem model with real data"""
        
        # Get real area data
        scenario_data = real_responses["minimal_dates_only"]
        area_data = scenario_data["response_data"]["items"][0]["areas"][0]
        
        # Create model from real data
        area_item = QuotaAreaItem(**area_data)
        
        # Verify all fields are correctly mapped
        assert area_item.label == "routing_old"
        assert area_item.name == "Planning"
        assert area_item.maxAvailable == 47539
        assert area_item.otherActivities == 0
        assert area_item.quota is None
        assert area_item.quotaPercent is None
        assert area_item.minQuota == 0
        assert area_item.used == 0
        assert area_item.bookedActivities == 0
        
        # Test area with quota set
        quota_area_data = real_responses["minimal_dates_only"]["response_data"]["items"][0]["areas"][3]
        quota_area = QuotaAreaItem(**quota_area_data)
        
        assert quota_area.label == "South Florida"
        assert quota_area.quota == 0
        assert quota_area.quotaPercent == 0
        assert quota_area.usedQuotaPercent == 0
    
    def test_csv_list_conversion_edge_cases(self):
        """Test CsvList conversion edge cases"""
        
        # Empty list
        empty_csv = CsvList.from_list([])
        assert empty_csv.value == ""
        assert empty_csv.to_list() == []
        
        # Single item
        single_csv = CsvList.from_list(["FLUSA"])
        assert single_csv.value == "FLUSA"
        assert single_csv.to_list() == ["FLUSA"]
        
        # Multiple items with spaces
        spaced_csv = CsvList(value="FLUSA, CAUSA , EST")
        assert spaced_csv.to_list() == ["FLUSA", "CAUSA", "EST"]
        
        # Empty string handling
        empty_string_csv = CsvList(value="")
        assert empty_string_csv.to_list() == []
        
        # String representation
        test_csv = CsvList.from_list(["FLUSA", "CAUSA"])
        assert str(test_csv) == "FLUSA,CAUSA"
        assert "CsvList(value='FLUSA,CAUSA'" in repr(test_csv)


class TestQuotaAPIInputFormats:
    """Test different input formats for quota API"""
    
    @pytest.fixture
    def ofsc_instance(self):
        return OFSC(clientID="test", secret="test", companyName="test")
    
    def test_different_input_formats(self, ofsc_instance):
        """Test that different input formats all work correctly"""
        
        mock_response_data = {"items": [{"date": "2025-06-25", "areas": []}]}
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Test 1: List input
            ofsc_instance.capacity.getQuota(
                dates=["2025-06-25"],
                areas=["FLUSA", "CAUSA"]
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
            
            # Test 2: CSV string input
            mock_get.reset_mock()
            ofsc_instance.capacity.getQuota(
                dates="2025-06-25",
                areas="FLUSA,CAUSA"
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
            
            # Test 3: CsvList input
            mock_get.reset_mock()
            ofsc_instance.capacity.getQuota(
                dates=CsvList.from_list(["2025-06-25"]),
                areas=CsvList.from_list(["FLUSA", "CAUSA"])
            )
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["areas"] == "FLUSA,CAUSA"
    
    def test_optional_parameters_handling(self, ofsc_instance):
        """Test that optional parameters are handled correctly"""
        
        mock_response_data = {"items": []}
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            # Minimal call - only dates
            ofsc_instance.capacity.getQuota(dates=["2025-06-25"])
            
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            
            # Should only have dates
            assert "dates" in params
            assert "areas" not in params
            assert "categories" not in params
            assert "aggregateResults" not in params