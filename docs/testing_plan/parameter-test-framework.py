# tests/utils/parameter_testing.py
"""Parameter testing utilities and data structures"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Callable
from enum import Enum
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

class TestCategory(Enum):
    """Test case categories"""
    HAPPY_PATH = "happy_path"
    BOUNDARY = "boundary"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class ParameterTestCase:
    """Single parameter test case"""
    test_id: str
    description: str
    category: TestCategory
    parameters: Dict[str, Any]
    expected_status: int = 200
    expected_error: Optional[str] = None
    expected_response: Optional[Dict[str, Any]] = None
    should_cleanup: bool = True
    skip_reason: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class EndpointTestSuite:
    """Complete test suite for an endpoint"""
    endpoint_name: str
    method: str
    path_template: str
    test_cases: List[ParameterTestCase]
    setup_required: Optional[Callable] = None
    teardown_required: Optional[Callable] = None
    rate_limit: int = 10
    
    def get_cases_by_category(self, category: TestCategory) -> List[ParameterTestCase]:
        """Get test cases filtered by category"""
        return [tc for tc in self.test_cases if tc.category == category]
    
    def get_cases_by_tag(self, tag: str) -> List[ParameterTestCase]:
        """Get test cases filtered by tag"""
        return [tc for tc in self.test_cases if tag in tc.tags]

class ParameterGenerator:
    """Generate test parameters dynamically"""
    
    # Define boundaries for common field types
    BOUNDARIES = {
        "string": {
            "min_length": 1,
            "max_length": 255,
            "max_text_length": 4000
        },
        "integer": {
            "min": 0,
            "max": 2147483647
        },
        "duration": {
            "min": 1,
            "max": 1440  # 24 hours in minutes
        },
        "array": {
            "min_items": 0,
            "max_items": 50
        },
        "date": {
            "min": datetime(2000, 1, 1),
            "max": datetime(2099, 12, 31)
        }
    }
    
    @classmethod
    def generate_string_boundaries(cls, field_name: str, 
                                 nullable: bool = False,
                                 max_length: int = 255) -> List[tuple]:
        """Generate boundary test cases for string fields"""
        cases = []
        
        if nullable:
            cases.append((f"{field_name}_null", None, True))
        
        cases.extend([
            (f"{field_name}_empty", "", False),
            (f"{field_name}_single_char", "A", True),
            (f"{field_name}_max_length", "A" * max_length, True),
            (f"{field_name}_over_max", "A" * (max_length + 1), False),
            (f"{field_name}_whitespace", "   ", False),
            (f"{field_name}_special_chars", "Test & <> \"' \n\t", True),
            (f"{field_name}_unicode", "Test 测试 🚀", True),
        ])
        
        return cases
    
    @classmethod
    def generate_numeric_boundaries(cls, field_name: str,
                                  min_value: int = 0,
                                  max_value: int = None,
                                  nullable: bool = False) -> List[tuple]:
        """Generate boundary test cases for numeric fields"""
        if max_value is None:
            max_value = cls.BOUNDARIES["integer"]["max"]
        
        cases = []
        
        if nullable:
            cases.append((f"{field_name}_null", None, True))
        
        cases.extend([
            (f"{field_name}_min", min_value, True),
            (f"{field_name}_max", max_value, True),
            (f"{field_name}_below_min", min_value - 1, False),
            (f"{field_name}_above_max", max_value + 1, False),
            (f"{field_name}_zero", 0, min_value <= 0),
            (f"{field_name}_negative", -1, min_value < 0),
        ])
        
        return cases
    
    @classmethod
    def generate_date_boundaries(cls, field_name: str,
                               allow_past: bool = True,
                               allow_future: bool = True) -> List[tuple]:
        """Generate boundary test cases for date fields"""
        now = datetime.now()
        cases = []
        
        cases.extend([
            (f"{field_name}_current", now.isoformat(), True),
            (f"{field_name}_invalid_format", "not-a-date", False),
            (f"{field_name}_invalid_date", "2024-13-01", False),
        ])
        
        if allow_past:
            cases.extend([
                (f"{field_name}_past", (now - timedelta(days=365)).isoformat(), True),
                (f"{field_name}_far_past", "1999-12-31T23:59:59", False),
            ])
        else:
            cases.append((f"{field_name}_past", (now - timedelta(days=1)).isoformat(), False))
        
        if allow_future:
            cases.extend([
                (f"{field_name}_future", (now + timedelta(days=365)).isoformat(), True),
                (f"{field_name}_far_future", "2100-01-01T00:00:00", False),
            ])
        else:
            cases.append((f"{field_name}_future", (now + timedelta(days=1)).isoformat(), False))
        
        return cases
    
    @classmethod
    def generate_array_boundaries(cls, field_name: str,
                                item_generator: Callable,
                                min_items: int = 0,
                                max_items: int = 50) -> List[tuple]:
        """Generate boundary test cases for array fields"""
        cases = [
            (f"{field_name}_empty", [], min_items == 0),
            (f"{field_name}_single", [item_generator()], True),
            (f"{field_name}_min_items", [item_generator() for _ in range(min_items)], True),
            (f"{field_name}_max_items", [item_generator() for _ in range(max_items)], True),
        ]
        
        if max_items < 1000:  # Prevent huge arrays
            cases.append(
                (f"{field_name}_over_max", [item_generator() for _ in range(max_items + 1)], False)
            )
        
        return cases
    
    @staticmethod
    def generate_activity_params(scenario: str = "basic") -> Dict[str, Any]:
        """Generate activity-specific test parameters"""
        scenarios = {
            "basic": {
                "name": fake.catch_phrase(),
                "activityType": "service",
                "duration": 60,
                "timeSlot": "all-day"
            },
            "detailed": {
                "name": fake.catch_phrase(),
                "activityType": random.choice(["service", "install", "repair"]),
                "duration": random.choice([30, 60, 90, 120]),
                "timeSlot": random.choice(["all-day", "AM", "PM"]),
                "workZone": fake.city(),
                "skills": [fake.job() for _ in range(random.randint(1, 3))],
                "inventory": {
                    "parts": [{"id": f"PART{i}", "quantity": random.randint(1, 5)} 
                             for i in range(random.randint(0, 3))]
                }
            },
            "boundary_duration": {
                "name": "Boundary Test Activity",
                "activityType": "service",
                "duration": 1440,  # Max 24 hours
                "timeSlot": "all-day"
            }
        }
        
        return scenarios.get(scenario, scenarios["basic"])
    
    @staticmethod
    def generate_resource_params(scenario: str = "basic") -> Dict[str, Any]:
        """Generate resource-specific test parameters"""
        scenarios = {
            "basic": {
                "name": fake.name(),
                "resourceType": "technician",
                "externalId": fake.uuid4()[:8]
            },
            "detailed": {
                "name": fake.name(),
                "resourceType": random.choice(["technician", "contractor"]),
                "externalId": fake.uuid4()[:8],
                "email": fake.email(),
                "phone": fake.phone_number(),
                "skills": [fake.job() for _ in range(random.randint(2, 5))],
                "workSchedule": {
                    "monday": {"start": "08:00", "end": "17:00"},
                    "tuesday": {"start": "08:00", "end": "17:00"},
                    "wednesday": {"start": "08:00", "end": "17:00"},
                    "thursday": {"start": "08:00", "end": "17:00"},
                    "friday": {"start": "08:00", "end": "17:00"}
                }
            }
        }
        
        return scenarios.get(scenario, scenarios["basic"])

# Pairwise combination testing utility
def generate_pairwise_combinations(parameters: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Generate pairwise parameter combinations using AllPairs algorithm"""
    try:
        from allpairspy import AllPairs
        
        combinations = []
        for pairs in AllPairs(parameters.values()):
            combo = dict(zip(parameters.keys(), pairs))
            combinations.append(combo)
        
        return combinations
    except ImportError:
        # Fallback to simple cartesian product for small sets
        import itertools
        
        keys = list(parameters.keys())
        values = [parameters[k] for k in keys]
        
        # Limit to reasonable number of combinations
        if sum(len(v) for v in values) > 20:
            # Sample instead of full product
            combinations = []
            for _ in range(min(50, 2 ** len(keys))):
                combo = {k: random.choice(parameters[k]) for k in keys}
                if combo not in combinations:
                    combinations.append(combo)
            return combinations
        
        # Full product for small sets
        return [dict(zip(keys, combo)) for combo in itertools.product(*values)]