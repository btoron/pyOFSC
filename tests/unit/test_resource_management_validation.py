"""Validation tests for resource management models in OFSC v3.0."""

# Remove unused imports

from ofsc.models.metadata import (
    ResourceType,
    ResourceTypeListResponse,
    InventoryType,
    InventoryTypeListResponse,
    WorksSkillAssignments,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    EnumerationValue,
    EnumerationValueList,
    Application,
    ApplicationListResponse,
    ApplicationsResourcestoAllow,
)
from ofsc.models.base import (
    BaseOFSResponse,
    OFSResponseList,
    TranslationList,
    Translation,
)


class TestResourceManagementModelsValidation:
    """Test validation for resource management models."""

    def test_resource_type_validation(self):
        """Test ResourceType model validation."""
        resource_type = ResourceType(
            label="Field Technician", name="FIELD_TECH", active=True, role="technician"
        )

        assert resource_type.label == "Field Technician"
        assert resource_type.name == "FIELD_TECH"
        assert resource_type.active is True
        assert resource_type.role == "technician"
        # translations has default value
        assert resource_type.translations is not None

    def test_resource_type_optional_fields(self):
        """Test ResourceType with various configurations."""
        # Test with custom translations
        resource_type_with_translation = ResourceType(
            label="Supervisor",
            name="SUPERVISOR",
            active=False,
            role="supervisor",
            translations=TranslationList(
                [
                    Translation(language="en", name="Supervisor"),
                    Translation(language="es", name="Supervisor"),
                ]
            ),
        )

        assert resource_type_with_translation.label == "Supervisor"
        assert resource_type_with_translation.name == "SUPERVISOR"
        assert resource_type_with_translation.active is False
        assert resource_type_with_translation.role == "supervisor"
        assert len(resource_type_with_translation.translations.root) == 2

    def test_resource_type_list_validation(self):
        """Test ResourceTypeListResponse model validation."""
        resource_types = ResourceTypeListResponse(
            items=[
                ResourceType(
                    label="Senior Technician",
                    name="SENIOR_TECH",
                    active=True,
                    role="technician",
                ),
                ResourceType(
                    label="Junior Technician",
                    name="JUNIOR_TECH",
                    active=True,
                    role="technician",
                ),
            ],
            totalResults=2,
            hasMore=False,
        )

        assert len(resource_types.items) == 2
        assert resource_types.items[0].label == "Senior Technician"
        assert resource_types.items[0].name == "SENIOR_TECH"
        assert resource_types.items[0].role == "technician"
        assert resource_types.items[1].label == "Junior Technician"
        assert resource_types.items[1].name == "JUNIOR_TECH"
        assert resource_types.items[1].active is True

    def test_inventory_type_validation(self):
        """Test InventoryType model validation."""
        inventory_type = InventoryType(
            label="Cable TV Equipment",
            name="CATV_EQUIP",
            unitOfMeasurement="piece",
            nonSerialized=True,
            quantityPrecision=2,
        )

        assert inventory_type.label == "Cable TV Equipment"
        assert inventory_type.name == "CATV_EQUIP"
        assert inventory_type.unitOfMeasurement == "piece"
        assert inventory_type.nonSerialized is True
        assert inventory_type.quantityPrecision == 2
        assert inventory_type.active is True  # Default value

    def test_inventory_type_list_validation(self):
        """Test InventoryTypeListResponse model validation."""
        inventory_types = InventoryTypeListResponse(
            items=[
                InventoryType(label="Cables", name="CABLES", unitOfMeasurement="meter"),
                InventoryType(
                    label="Connectors", name="CONNECTORS", unitOfMeasurement="piece"
                ),
            ],
            totalResults=2,
            hasMore=False,
        )

        assert len(inventory_types.items) == 2
        assert inventory_types.items[0].label == "Cables"
        assert inventory_types.items[0].unitOfMeasurement == "meter"
        assert inventory_types.items[1].label == "Connectors"
        assert inventory_types.items[1].unitOfMeasurement == "piece"

    def test_inventory_type_list_response_validation(self):
        """Test InventoryTypeListResponse model validation."""
        inventory_response = InventoryTypeListResponse(
            items=[
                InventoryType(label="Modem", name="MODEM", nonSerialized=True),
                InventoryType(label="Router", name="ROUTER", nonSerialized=True),
            ]
        )

        assert len(inventory_response.items) == 2
        assert inventory_response.items[0].label == "Modem"
        assert inventory_response.items[0].nonSerialized is True
        assert inventory_response.items[1].label == "Router"
        assert inventory_response.items[1].nonSerialized is True

    def test_work_skill_assignments_validation(self):
        """Test WorksSkillAssignments model validation."""
        skill_assignment = WorksSkillAssignments(
            workSkillLabel="Electrical Wiring", level=5
        )

        assert skill_assignment.workSkillLabel == "Electrical Wiring"
        assert skill_assignment.level == 5

    def test_work_skill_group_validation(self):
        """Test WorkSkillGroup model validation."""
        skill_group = WorkSkillGroup(
            label="Electrical Skills",
            name="ELECTRICAL",
            workSkills=[WorksSkillAssignments(workSkillLabel="Wiring", level=3)],
            active=True,
        )

        assert skill_group.label == "Electrical Skills"
        assert skill_group.name == "ELECTRICAL"
        assert len(skill_group.workSkills) == 1
        assert skill_group.workSkills[0].workSkillLabel == "Wiring"
        assert skill_group.active is True

    def test_work_skill_assignments_validation(self):
        """Test WorksSkillAssignments model validation."""
        # Test individual assignment
        assignment1 = WorksSkillAssignments(workSkillLabel="Plumbing", level=3)
        assignment2 = WorksSkillAssignments(workSkillLabel="HVAC", level=4)

        assert assignment1.workSkillLabel == "Plumbing"
        assert assignment1.level == 3
        assert assignment2.workSkillLabel == "HVAC"
        assert assignment2.level == 4

        # Test as part of WorkSkillGroup
        skill_group = WorkSkillGroup(
            label="Technical Group",
            name="TECH_GROUP",
            workSkills=[assignment1, assignment2],
        )

        assert len(skill_group.workSkills) == 2
        assert skill_group.workSkills[0].workSkillLabel == "Plumbing"
        assert skill_group.workSkills[1].workSkillLabel == "HVAC"

    def test_work_skill_group_list_validation(self):
        """Test WorkSkillGroupListResponse model validation."""
        group_list = WorkSkillGroupListResponse(
            items=[
                WorkSkillGroup(label="Safety Skills", name="SAFETY", active=True),
                WorkSkillGroup(label="Technical Skills", name="TECHNICAL", active=True),
            ],
            totalResults=2,
            hasMore=False,
        )

        assert len(group_list.items) == 2
        assert group_list.items[0].label == "Safety Skills"
        assert group_list.items[0].name == "SAFETY"
        assert group_list.items[1].label == "Technical Skills"
        assert group_list.items[1].name == "TECHNICAL"

    def test_work_skill_group_list_response_validation(self):
        """Test WorkSkillGroupListResponse model validation."""
        group_response = WorkSkillGroupListResponse(
            items=[WorkSkillGroup(label="Communication Skills", name="COMMUNICATION")]
        )

        assert len(group_response.items) == 1
        assert group_response.items[0].label == "Communication Skills"
        assert group_response.items[0].name == "COMMUNICATION"

    def test_enumeration_value_validation(self):
        """Test EnumerationValue model validation."""
        enum_value = EnumerationValue(label="High Priority", name="HIGH", active=True)

        assert enum_value.name == "HIGH"
        assert enum_value.label == "High Priority"
        assert enum_value.active is True

    def test_enumeration_value_list_validation(self):
        """Test EnumerationValueList model validation."""
        enum_list = EnumerationValueList(
            items=[
                EnumerationValue(name="LOW", label="Low Priority"),
                EnumerationValue(name="MEDIUM", label="Medium Priority"),
                EnumerationValue(name="HIGH", label="High Priority"),
            ]
        )

        assert len(enum_list.items) == 3
        assert enum_list.items[0].name == "LOW"
        assert enum_list.items[0].label == "Low Priority"
        assert enum_list.items[1].name == "MEDIUM"
        assert enum_list.items[1].label == "Medium Priority"
        assert enum_list.items[2].name == "HIGH"
        assert enum_list.items[2].label == "High Priority"

    def test_applications_resources_to_allow_validation(self):
        """Test ApplicationsResourcestoAllow model validation."""
        resource_allow = ApplicationsResourcestoAllow(
            userType="FIELD_TECH", resourceTypes=["TECH001", "TECH002"]
        )

        assert resource_allow.userType == "FIELD_TECH"
        assert len(resource_allow.resourceTypes) == 2
        assert "TECH001" in resource_allow.resourceTypes
        assert "TECH002" in resource_allow.resourceTypes

    def test_application_validation(self):
        """Test Application model validation."""
        application = Application(
            label="Mobile Field App",
            name="MOBILE_APP",
            activityTypes=["Installation", "Maintenance"],
            resourceTypes=["FIELD_TECH", "SUPERVISOR"],
            resourcesAllowed=[
                ApplicationsResourcestoAllow(
                    userType="FIELD_TECH", resourceTypes=["TECH001"]
                )
            ],
            defaultApplication=False,
        )

        assert application.label == "Mobile Field App"
        assert application.name == "MOBILE_APP"
        assert len(application.activityTypes) == 2
        assert "Installation" in application.activityTypes
        assert len(application.resourceTypes) == 2
        assert "FIELD_TECH" in application.resourceTypes
        assert len(application.resourcesAllowed) == 1
        assert application.resourcesAllowed[0].userType == "FIELD_TECH"
        assert application.defaultApplication is False

    def test_application_list_response_validation(self):
        """Test ApplicationListResponse model validation."""
        app_response = ApplicationListResponse(
            items=[
                Application(label="Dispatcher Console", name="DISPATCH_CONSOLE"),
                Application(label="Customer Portal", name="CUSTOMER_PORTAL"),
            ]
        )

        assert len(app_response.items) == 2
        assert app_response.items[0].label == "Dispatcher Console"
        assert app_response.items[0].name == "DISPATCH_CONSOLE"
        assert app_response.items[1].label == "Customer Portal"
        assert app_response.items[1].name == "CUSTOMER_PORTAL"

    def test_resource_management_models_inherit_base_ofs_response(self):
        """Test that resource management models inherit from BaseOFSResponse."""
        models_to_test = [
            ResourceType,
            InventoryType,
            WorksSkillAssignments,
            WorkSkillGroup,
            EnumerationValue,
            ApplicationsResourcestoAllow,
            Application,
        ]

        for model_class in models_to_test:
            assert issubclass(model_class, BaseOFSResponse), (
                f"{model_class.__name__} should inherit from BaseOFSResponse"
            )

    def test_list_response_models_inherit_ofs_response_list(self):
        """Test that list response models inherit from OFSResponseList."""
        list_models_to_test = [
            ResourceTypeListResponse,
            InventoryTypeListResponse,
            WorkSkillGroupListResponse,
            EnumerationValueList,
            ApplicationListResponse,
        ]

        for model_class in list_models_to_test:
            assert issubclass(model_class, OFSResponseList), (
                f"{model_class.__name__} should inherit from OFSResponseList"
            )

    def test_complex_resource_management_scenario(self):
        """Test complex resource management scenario with nested relationships."""
        # Create a comprehensive resource management structure
        complex_application = Application(
            label="Advanced Field Service App",
            name="ADVANCED_FSA",
            activityTypes=["Installation", "Maintenance", "Repair"],
            resourceTypes=["SENIOR_TECH", "JUNIOR_TECH", "SUPERVISOR"],
            resourcesAllowed=[
                ApplicationsResourcestoAllow(
                    userType="SENIOR_TECH", resourceTypes=["TECH001", "TECH002"]
                ),
                ApplicationsResourcestoAllow(
                    userType="JUNIOR_TECH", resourceTypes=["TECH003"]
                ),
                ApplicationsResourcestoAllow(
                    userType="SUPERVISOR", resourceTypes=["SUP001"]
                ),
            ],
            defaultApplication=False,
        )

        # Validate the complex structure
        assert complex_application.label == "Advanced Field Service App"
        assert complex_application.name == "ADVANCED_FSA"
        assert len(complex_application.resourcesAllowed) == 3
        assert len(complex_application.activityTypes) == 3
        assert "Installation" in complex_application.activityTypes

        # Validate senior tech access
        senior_access = complex_application.resourcesAllowed[0]
        assert senior_access.userType == "SENIOR_TECH"
        assert len(senior_access.resourceTypes) == 2
        assert "TECH001" in senior_access.resourceTypes

        # Validate junior tech access
        junior_access = complex_application.resourcesAllowed[1]
        assert junior_access.userType == "JUNIOR_TECH"
        assert len(junior_access.resourceTypes) == 1
        assert "TECH003" in junior_access.resourceTypes

        # Validate supervisor access
        supervisor_access = complex_application.resourcesAllowed[2]
        assert supervisor_access.userType == "SUPERVISOR"
        assert "SUP001" in supervisor_access.resourceTypes

    def test_resource_management_model_serialization(self):
        """Test resource management model serialization."""
        resource_type = ResourceType(
            label="Mobile Technician",
            name="MOBILE_TECH",
            active=True,
            role="technician",
        )

        serialized = resource_type.model_dump()
        assert "label" in serialized
        assert "name" in serialized
        assert "active" in serialized
        assert "role" in serialized
        assert serialized["label"] == "Mobile Technician"
        assert serialized["name"] == "MOBILE_TECH"
        assert serialized["active"] is True
        assert serialized["role"] == "technician"

    def test_resource_management_extra_fields_handling(self):
        """Test resource management models handle extra fields according to their configuration."""
        # Test models with extra="allow" like Application and WorkSkillGroup
        app_data = {
            "label": "Specialist App",
            "name": "SPECIALIST_APP",
            "customField1": "custom_value",
            "numericField": 42,
            "booleanField": True,
        }

        application = Application(**app_data)
        assert application.label == "Specialist App"
        assert application.name == "SPECIALIST_APP"

        # Test that WorkSkillGroup no longer allows extra fields (now uses default extra="forbid")
        # Just test the basic functionality
        skill_group = WorkSkillGroup(label="Specialist Group", name="SPECIALIST_GROUP")
        assert skill_group.label == "Specialist Group"
        assert skill_group.name == "SPECIALIST_GROUP"

        # Test models without extra="allow" (like ResourceType) don't accept extra fields
        resource_data = {
            "label": "Specialist",
            "name": "SPECIALIST",
            "active": True,
            "role": "specialist",
        }

        resource_type = ResourceType(**resource_data)
        assert resource_type.label == "Specialist"
        assert resource_type.name == "SPECIALIST"
        assert resource_type.active is True
        assert resource_type.role == "specialist"

    def test_work_skill_proficiency_levels(self):
        """Test work skill assignments with different proficiency levels."""
        proficiency_levels = [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert",
            "Master",
        ]

        assignments = []
        for i, level in enumerate(proficiency_levels):
            assignment = WorksSkillAssignments(
                workSkillLabel=f"Skill_{i + 1}",
                level=i + 1,  # level expects an integer
            )
            assignments.append(assignment)

        # Validate all assignments
        assert len(assignments) == 5
        for i, assignment in enumerate(assignments):
            assert assignment.level == i + 1
            assert assignment.workSkillLabel == f"Skill_{i + 1}"

    def test_inventory_type_units_and_categories(self):
        """Test inventory types with various units and categories."""
        inventory_types = [
            InventoryType(
                label="Ethernet Cable",
                name="ETH_CABLE",
                unitOfMeasurement="meter",
                nonSerialized=True,
                quantityPrecision=2,
            ),
            InventoryType(
                label="WiFi Router",
                name="WIFI_ROUTER",
                unitOfMeasurement="piece",
                quantityPrecision=0,
                modelProperty="router_model",
            ),
            InventoryType(
                label="Installation Kit",
                name="INSTALL_KIT",
                unitOfMeasurement="kit",
                nonSerialized=False,
                active=False,
            ),
        ]

        # Validate different inventory configurations
        cable = inventory_types[0]
        assert cable.unitOfMeasurement == "meter"
        assert cable.nonSerialized is True
        assert cable.quantityPrecision == 2

        router = inventory_types[1]
        assert router.unitOfMeasurement == "piece"
        assert router.quantityPrecision == 0
        assert router.modelProperty == "router_model"

        kit = inventory_types[2]
        assert kit.unitOfMeasurement == "kit"
        assert kit.nonSerialized is False
        assert kit.active is False
