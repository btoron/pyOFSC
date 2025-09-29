"""
Model validation tests for Metadata API responses.

This file contains comprehensive validation tests for all Metadata API models
against real API response examples.

Generated on: 2025-07-25 12:46:44 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.metadata import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    Application,
    ApplicationApiAccess,
    ApplicationApiAccessListResponse,
    ApplicationListResponse,
    EnumerationValue,
    EnumerationValueList,
    Form,
    FormListResponse,
    InventoryType,
    InventoryTypeListResponse,
    Language,
    LanguageListResponse,
    LinkTemplate,
    LinkTemplateListResponse,
    NonWorkingReason,
    NonWorkingReasonListResponse,
    Organization,
    OrganizationListResponse,
    PropertyListResponse,
    PropertyResponse,
    ResourceType,
    ResourceTypeListResponse,
    RoutingPlan,
    RoutingPlanExportResponse,
    RoutingPlanListResponse,
    RoutingProfile,
    RoutingProfileListResponse,
    Shift,
    ShiftListResponse,
    TimeSlot,
    TimeSlotListResponse,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    WorkZoneKeyResponse,
    Workskill,
    WorkskillCondition,
    WorkskillConditionListResponse,
    WorkskillListResponse,
    Workzone,
    WorkzoneListResponse,
)


class TestMetadataModelsValidation:
    """Test Metadata API model validation against response examples."""

    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

    def test_form_validation(self, response_examples_path):
        """Validate Form model against saved response examples.

        Tests against endpoints: #28
        """
        response_files = [
            "28_get_forms_mobile_provider_request%238%23_mobile_provider_request_8_.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Form(**data)
                        self._validate_form_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Form validation failed for {filename}: {e}")

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Form(**item)
                            self._validate_form_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Form validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Form(**data)
                    self._validate_form_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Form validation failed for {filename}: {e}")

    def _validate_form_fields(self, model: Form, original_data: dict):
        """Validate specific fields for Form."""
        # Add model-specific field validations here
        assert hasattr(model, "label"), "Missing required field: label"
        assert hasattr(model, "name"), "Missing required field: name"

    def test_workskill_list_response_validation(self, response_examples_path):
        """Validate WorkskillListResponse model against saved response examples.

        Tests against endpoints: #74
        """
        response_files = [
            "74_get_work_skills.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = WorkskillListResponse(**data)
                        self._validate_workskill_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkskillListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workskill(**item)
                            print(f"✅ Validated {filename} item {idx} with Workskill")
                        except ValidationError as e:
                            pytest.fail(
                                f"Workskill validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkskillListResponse(**item)
                            self._validate_workskill_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkskillListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkskillListResponse(**data)
                    self._validate_workskill_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"WorkskillListResponse validation failed for {filename}: {e}"
                    )

    def _validate_workskill_list_response_fields(
        self, model: WorkskillListResponse, original_data: dict
    ):
        """Validate specific fields for WorkskillListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_application_list_response_validation(self, response_examples_path):
        """Validate ApplicationListResponse model against saved response examples.

        Tests against endpoints: #7
        """
        response_files = [
            "7_get_applications.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationListResponse(**data)
                        self._validate_application_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ApplicationListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Application(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with Application"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"Application validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationListResponse(**item)
                            self._validate_application_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ApplicationListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ApplicationListResponse(**data)
                    self._validate_application_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ApplicationListResponse validation failed for {filename}: {e}"
                    )

    def _validate_application_list_response_fields(
        self, model: ApplicationListResponse, original_data: dict
    ):
        """Validate specific fields for ApplicationListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_activity_type_list_response_validation(self, response_examples_path):
        """Validate ActivityTypeListResponse model against saved response examples.

        Tests against endpoints: #4
        """
        response_files = [
            "4_get_activity_types.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeListResponse(**data)
                        self._validate_activity_type_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ActivityTypeListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityType(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with ActivityType"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityType validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeListResponse(**item)
                            self._validate_activity_type_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityTypeListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeListResponse(**data)
                    self._validate_activity_type_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ActivityTypeListResponse validation failed for {filename}: {e}"
                    )

    def _validate_activity_type_list_response_fields(
        self, model: ActivityTypeListResponse, original_data: dict
    ):
        """Validate specific fields for ActivityTypeListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_application_api_access_list_response_validation(
        self, response_examples_path
    ):
        """Validate ApplicationApiAccessListResponse model against saved response examples.

        Tests against endpoints: #10
        """
        response_files = [
            "10_get_applications_demoauth_apiAccess_demoauth.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationApiAccessListResponse(**data)
                        self._validate_application_api_access_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ApplicationApiAccessListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationApiAccess(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with ApplicationApiAccess"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"ApplicationApiAccess validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationApiAccessListResponse(**item)
                            self._validate_application_api_access_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ApplicationApiAccessListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ApplicationApiAccessListResponse(**data)
                    self._validate_application_api_access_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ApplicationApiAccessListResponse validation failed for {filename}: {e}"
                    )

    def _validate_application_api_access_list_response_fields(
        self, model: ApplicationApiAccessListResponse, original_data: dict
    ):
        """Validate specific fields for ApplicationApiAccessListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_workskill_condition_list_response_validation(self, response_examples_path):
        """Validate WorkskillConditionListResponse model against saved response examples.

        Tests against endpoints: #68
        """
        response_files = [
            "68_get_work_skill_conditions.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = WorkskillConditionListResponse(**data)
                        self._validate_workskill_condition_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkskillConditionListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkskillCondition(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with WorkskillCondition"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkskillCondition validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkskillConditionListResponse(**item)
                            self._validate_workskill_condition_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkskillConditionListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkskillConditionListResponse(**data)
                    self._validate_workskill_condition_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"WorkskillConditionListResponse validation failed for {filename}: {e}"
                    )

    def _validate_workskill_condition_list_response_fields(
        self, model: WorkskillConditionListResponse, original_data: dict
    ):
        """Validate specific fields for WorkskillConditionListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_organization_validation(self, response_examples_path):
        """Validate Organization model against saved response examples.

        Tests against endpoints: #47
        """
        response_files = [
            "47_get_organizations_default_default.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Organization(**data)
                        self._validate_organization_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"Organization validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Organization(**item)
                            self._validate_organization_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Organization validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Organization(**data)
                    self._validate_organization_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Organization validation failed for {filename}: {e}")

    def _validate_organization_fields(self, model: Organization, original_data: dict):
        """Validate specific fields for Organization."""
        # Add model-specific field validations here
        assert hasattr(model, "label"), "Missing required field: label"
        assert hasattr(model, "type"), "Missing required field: type"
        assert hasattr(model, "translations"), "Missing required field: translations"
        if hasattr(model, "type") and getattr(model, "type") is not None:
            assert getattr(model, "type") in ["contractor", "inhouse"], (
                "Invalid enum value for type"
            )

    def test_resource_type_list_response_validation(self, response_examples_path):
        """Validate ResourceTypeListResponse model against saved response examples.

        Tests against endpoints: #56
        """
        response_files = [
            "56_get_resource_types.json",
            "56_resource_types.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ResourceTypeListResponse(**data)
                        self._validate_resource_type_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ResourceTypeListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceType(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with ResourceType"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"ResourceType validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceTypeListResponse(**item)
                            self._validate_resource_type_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ResourceTypeListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ResourceTypeListResponse(**data)
                    self._validate_resource_type_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ResourceTypeListResponse validation failed for {filename}: {e}"
                    )

    def _validate_resource_type_list_response_fields(
        self, model: ResourceTypeListResponse, original_data: dict
    ):
        """Validate specific fields for ResourceTypeListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_work_skill_group_list_response_validation(self, response_examples_path):
        """Validate WorkSkillGroupListResponse model against saved response examples.

        Tests against endpoints: #70
        """
        response_files = [
            "70_get_work_skill_groups.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = WorkSkillGroupListResponse(**data)
                        self._validate_work_skill_group_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkSkillGroupListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkSkillGroup(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with WorkSkillGroup"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkSkillGroup validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkSkillGroupListResponse(**item)
                            self._validate_work_skill_group_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkSkillGroupListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkSkillGroupListResponse(**data)
                    self._validate_work_skill_group_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"WorkSkillGroupListResponse validation failed for {filename}: {e}"
                    )

    def _validate_work_skill_group_list_response_fields(
        self, model: WorkSkillGroupListResponse, original_data: dict
    ):
        """Validate specific fields for WorkSkillGroupListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_non_working_reason_list_response_validation(self, response_examples_path):
        """Validate NonWorkingReasonListResponse model against saved response examples.

        Tests against endpoints: #45
        """
        response_files = [
            "45_get_non_working_reasons.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = NonWorkingReasonListResponse(**data)
                        self._validate_non_working_reason_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"NonWorkingReasonListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = NonWorkingReason(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with NonWorkingReason"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"NonWorkingReason validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = NonWorkingReasonListResponse(**item)
                            self._validate_non_working_reason_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"NonWorkingReasonListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = NonWorkingReasonListResponse(**data)
                    self._validate_non_working_reason_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"NonWorkingReasonListResponse validation failed for {filename}: {e}"
                    )

    def _validate_non_working_reason_list_response_fields(
        self, model: NonWorkingReasonListResponse, original_data: dict
    ):
        """Validate specific fields for NonWorkingReasonListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_property_list_response_validation(self, response_examples_path):
        """Validate PropertyListResponse model against saved response examples.

        Tests against endpoints: #50
        """
        response_files = [
            "50_get_properties.json",
            "50_properties.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = PropertyListResponse(**data)
                        self._validate_property_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"PropertyListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = PropertyListResponse(**item)
                            self._validate_property_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"PropertyListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = PropertyListResponse(**data)
                    self._validate_property_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"PropertyListResponse validation failed for {filename}: {e}"
                    )

    def _validate_property_list_response_fields(
        self, model: PropertyListResponse, original_data: dict
    ):
        """Validate specific fields for PropertyListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_work_zone_key_response_validation(self, response_examples_path):
        """Validate WorkZoneKeyResponse model against saved response examples.

        Tests against endpoints: #86
        """
        response_files = [
            "86_get_the_work_zone_key.json",
            "86_get_workZoneKey.json",
            "86_workzone_keys.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = WorkZoneKeyResponse(**data)
                        self._validate_work_zone_key_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkZoneKeyResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkZoneKeyResponse(**item)
                            self._validate_work_zone_key_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkZoneKeyResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkZoneKeyResponse(**data)
                    self._validate_work_zone_key_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"WorkZoneKeyResponse validation failed for {filename}: {e}"
                    )

    def _validate_work_zone_key_response_fields(
        self, model: WorkZoneKeyResponse, original_data: dict
    ):
        """Validate specific fields for WorkZoneKeyResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_group_list_response_validation(self, response_examples_path):
        """Validate ActivityTypeGroupListResponse model against saved response examples.

        Tests against endpoints: #1
        """
        response_files = [
            "1_get_activity_type_groups.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeGroupListResponse(**data)
                        self._validate_activity_type_group_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ActivityTypeGroupListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeGroup(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with ActivityTypeGroup"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityTypeGroup validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeGroupListResponse(**item)
                            self._validate_activity_type_group_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityTypeGroupListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeGroupListResponse(**data)
                    self._validate_activity_type_group_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ActivityTypeGroupListResponse validation failed for {filename}: {e}"
                    )

    def _validate_activity_type_group_list_response_fields(
        self, model: ActivityTypeGroupListResponse, original_data: dict
    ):
        """Validate specific fields for ActivityTypeGroupListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_routing_profile_list_response_validation(self, response_examples_path):
        """Validate RoutingProfileListResponse model against saved response examples.

        Tests against endpoints: #57
        """
        response_files = [
            "57_get_routing_profiles.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = RoutingProfileListResponse(**data)
                        self._validate_routing_profile_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"RoutingProfileListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingProfile(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with RoutingProfile"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"RoutingProfile validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingProfileListResponse(**item)
                            self._validate_routing_profile_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"RoutingProfileListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = RoutingProfileListResponse(**data)
                    self._validate_routing_profile_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"RoutingProfileListResponse validation failed for {filename}: {e}"
                    )

    def _validate_routing_profile_list_response_fields(
        self, model: RoutingProfileListResponse, original_data: dict
    ):
        """Validate specific fields for RoutingProfileListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_application_validation(self, response_examples_path):
        """Validate Application model against saved response examples.

        Tests against endpoints: #8
        """
        response_files = [
            "8_get_applications_demoauth_demoauth.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Application(**data)
                        self._validate_application_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"Application validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Application(**item)
                            self._validate_application_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Application validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Application(**data)
                    self._validate_application_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Application validation failed for {filename}: {e}")

    def _validate_application_fields(self, model: Application, original_data: dict):
        """Validate specific fields for Application."""
        # Add model-specific field validations here
        if hasattr(model, "status") and getattr(model, "status") is not None:
            assert getattr(model, "status") in ["active", "inactive"], (
                "Invalid enum value for status"
            )

    def test_link_template_list_response_validation(self, response_examples_path):
        """Validate LinkTemplateListResponse model against saved response examples.

        Tests against endpoints: #35
        """
        response_files = [
            "35_get_link_templates.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = LinkTemplateListResponse(**data)
                        self._validate_link_template_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"LinkTemplateListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LinkTemplate(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with LinkTemplate"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"LinkTemplate validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LinkTemplateListResponse(**item)
                            self._validate_link_template_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"LinkTemplateListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = LinkTemplateListResponse(**data)
                    self._validate_link_template_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"LinkTemplateListResponse validation failed for {filename}: {e}"
                    )

    def _validate_link_template_list_response_fields(
        self, model: LinkTemplateListResponse, original_data: dict
    ):
        """Validate specific fields for LinkTemplateListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_inventory_type_validation(self, response_examples_path):
        """Validate InventoryType model against saved response examples.

        Tests against endpoints: #32
        """
        response_files = [
            "32_get_inventoryTypes_FIT5000_FIT5000.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = InventoryType(**data)
                        self._validate_inventory_type_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"InventoryType validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = InventoryType(**item)
                            self._validate_inventory_type_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"InventoryType validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = InventoryType(**data)
                    self._validate_inventory_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"InventoryType validation failed for {filename}: {e}")

    def _validate_inventory_type_fields(
        self, model: InventoryType, original_data: dict
    ):
        """Validate specific fields for InventoryType."""
        # Add model-specific field validations here
        assert hasattr(model, "label"), "Missing required field: label"
        assert hasattr(model, "name"), "Missing required field: name"
        assert hasattr(model, "active"), "Missing required field: active"

    def test_activity_type_group_validation(self, response_examples_path):
        """Validate ActivityTypeGroup model against saved response examples.

        Tests against endpoints: #2
        """
        response_files = [
            "2_get_activityTypeGroups_customer_customer.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeGroup(**data)
                        self._validate_activity_type_group_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ActivityTypeGroup validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeGroup(**item)
                            self._validate_activity_type_group_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityTypeGroup validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeGroup(**data)
                    self._validate_activity_type_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ActivityTypeGroup validation failed for {filename}: {e}"
                    )

    def _validate_activity_type_group_fields(
        self, model: ActivityTypeGroup, original_data: dict
    ):
        """Validate specific fields for ActivityTypeGroup."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_shift_list_response_validation(self, response_examples_path):
        """Validate ShiftListResponse model against saved response examples.

        Tests against endpoints: #63
        """
        response_files = [
            "63_get_shifts.json",
            "63_shifts.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = ShiftListResponse(**data)
                        self._validate_shift_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ShiftListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Shift(**item)
                            print(f"✅ Validated {filename} item {idx} with Shift")
                        except ValidationError as e:
                            pytest.fail(
                                f"Shift validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ShiftListResponse(**item)
                            self._validate_shift_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ShiftListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ShiftListResponse(**data)
                    self._validate_shift_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ShiftListResponse validation failed for {filename}: {e}"
                    )

    def _validate_shift_list_response_fields(
        self, model: ShiftListResponse, original_data: dict
    ):
        """Validate specific fields for ShiftListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_work_skill_group_validation(self, response_examples_path):
        """Validate WorkSkillGroup model against saved response examples.

        Tests against endpoints: #71
        """
        response_files = [
            "71_get_workSkillGroups_TEST_TEST.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = WorkSkillGroup(**data)
                        self._validate_work_skill_group_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkSkillGroup validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkSkillGroup(**item)
                            self._validate_work_skill_group_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkSkillGroup validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkSkillGroup(**data)
                    self._validate_work_skill_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"WorkSkillGroup validation failed for {filename}: {e}")

    def _validate_work_skill_group_fields(
        self, model: WorkSkillGroup, original_data: dict
    ):
        """Validate specific fields for WorkSkillGroup."""
        # Add model-specific field validations here
        assert hasattr(model, "assignToResource"), (
            "Missing required field: assignToResource"
        )
        assert hasattr(model, "addToCapacityCategory"), (
            "Missing required field: addToCapacityCategory"
        )
        assert hasattr(model, "active"), "Missing required field: active"

    def test_routing_plan_export_response_validation(self, response_examples_path):
        """Validate RoutingPlanExportResponse model against saved response examples.

        Tests against endpoints: #59
        """
        response_files = [
            "59_get_routingProfiles_MaintenanceRoutingProfile_plans_Optimization_custom-actions_export_MaintenanceRoutingProfile_Optimization.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = RoutingPlanExportResponse(**data)
                        self._validate_routing_plan_export_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"RoutingPlanExportResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingPlanExportResponse(**item)
                            self._validate_routing_plan_export_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"RoutingPlanExportResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = RoutingPlanExportResponse(**data)
                    self._validate_routing_plan_export_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"RoutingPlanExportResponse validation failed for {filename}: {e}"
                    )

    def _validate_routing_plan_export_response_fields(
        self, model: RoutingPlanExportResponse, original_data: dict
    ):
        """Validate specific fields for RoutingPlanExportResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_form_list_response_validation(self, response_examples_path):
        """Validate FormListResponse model against saved response examples.

        Tests against endpoints: #27
        """
        response_files = [
            "27_get_forms.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = FormListResponse(**data)
                        self._validate_form_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"FormListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Form(**item)
                            print(f"✅ Validated {filename} item {idx} with Form")
                        except ValidationError as e:
                            pytest.fail(
                                f"Form validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = FormListResponse(**item)
                            self._validate_form_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"FormListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = FormListResponse(**data)
                    self._validate_form_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"FormListResponse validation failed for {filename}: {e}"
                    )

    def _validate_form_list_response_fields(
        self, model: FormListResponse, original_data: dict
    ):
        """Validate specific fields for FormListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_workzone_list_response_validation(self, response_examples_path):
        """Validate WorkzoneListResponse model against saved response examples.

        Tests against endpoints: #78
        """
        response_files = [
            "78_get_work_zones.json",
            "78_workzones.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = WorkzoneListResponse(**data)
                        self._validate_workzone_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"WorkzoneListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workzone(**item)
                            print(f"✅ Validated {filename} item {idx} with Workzone")
                        except ValidationError as e:
                            pytest.fail(
                                f"Workzone validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkzoneListResponse(**item)
                            self._validate_workzone_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"WorkzoneListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = WorkzoneListResponse(**data)
                    self._validate_workzone_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"WorkzoneListResponse validation failed for {filename}: {e}"
                    )

    def _validate_workzone_list_response_fields(
        self, model: WorkzoneListResponse, original_data: dict
    ):
        """Validate specific fields for WorkzoneListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_language_list_response_validation(self, response_examples_path):
        """Validate LanguageListResponse model against saved response examples.

        Tests against endpoints: #34
        """
        response_files = [
            "34_get_languages.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = LanguageListResponse(**data)
                        self._validate_language_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"LanguageListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Language(**item)
                            print(f"✅ Validated {filename} item {idx} with Language")
                        except ValidationError as e:
                            pytest.fail(
                                f"Language validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LanguageListResponse(**item)
                            self._validate_language_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"LanguageListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = LanguageListResponse(**data)
                    self._validate_language_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"LanguageListResponse validation failed for {filename}: {e}"
                    )

    def _validate_language_list_response_fields(
        self, model: LanguageListResponse, original_data: dict
    ):
        """Validate specific fields for LanguageListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_enumeration_value_list_validation(self, response_examples_path):
        """Validate EnumerationValueList model against saved response examples.

        Tests against endpoints: #54
        """
        response_files = [
            "54_get_properties_complete_code_enumerationList_complete_code.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = EnumerationValueList(**data)
                        self._validate_enumeration_value_list_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"EnumerationValueList validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = EnumerationValue(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with EnumerationValue"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"EnumerationValue validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = EnumerationValueList(**item)
                            self._validate_enumeration_value_list_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"EnumerationValueList validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = EnumerationValueList(**data)
                    self._validate_enumeration_value_list_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"EnumerationValueList validation failed for {filename}: {e}"
                    )

    def _validate_enumeration_value_list_fields(
        self, model: EnumerationValueList, original_data: dict
    ):
        """Validate specific fields for EnumerationValueList."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_shift_validation(self, response_examples_path):
        """Validate Shift model against saved response examples.

        Tests against endpoints: #64
        """
        response_files = [
            "64_get_shift.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Shift(**data)
                        self._validate_shift_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Shift validation failed for {filename}: {e}")

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Shift(**item)
                            self._validate_shift_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Shift validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Shift(**data)
                    self._validate_shift_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Shift validation failed for {filename}: {e}")

    def _validate_shift_fields(self, model: Shift, original_data: dict):
        """Validate specific fields for Shift."""
        # Add model-specific field validations here
        assert hasattr(model, "name"), "Missing required field: name"
        assert hasattr(model, "active"), "Missing required field: active"
        assert hasattr(model, "type"), "Missing required field: type"

    def test_workskill_validation(self, response_examples_path):
        """Validate Workskill model against saved response examples.

        Tests against endpoints: #75
        """
        response_files = [
            "75_get_workSkills_EST_EST.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Workskill(**data)
                        self._validate_workskill_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Workskill validation failed for {filename}: {e}")

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workskill(**item)
                            self._validate_workskill_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Workskill validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Workskill(**data)
                    self._validate_workskill_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Workskill validation failed for {filename}: {e}")

    def _validate_workskill_fields(self, model: Workskill, original_data: dict):
        """Validate specific fields for Workskill."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_time_slot_list_response_validation(self, response_examples_path):
        """Validate TimeSlotListResponse model against saved response examples.

        Tests against endpoints: #67
        """
        response_files = [
            "67_get_time_slots.json",
            "67_timeslots.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = TimeSlotListResponse(**data)
                        self._validate_time_slot_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"TimeSlotListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = TimeSlot(**item)
                            print(f"✅ Validated {filename} item {idx} with TimeSlot")
                        except ValidationError as e:
                            pytest.fail(
                                f"TimeSlot validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = TimeSlotListResponse(**item)
                            self._validate_time_slot_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"TimeSlotListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = TimeSlotListResponse(**data)
                    self._validate_time_slot_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"TimeSlotListResponse validation failed for {filename}: {e}"
                    )

    def _validate_time_slot_list_response_fields(
        self, model: TimeSlotListResponse, original_data: dict
    ):
        """Validate specific fields for TimeSlotListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_link_template_validation(self, response_examples_path):
        """Validate LinkTemplate model against saved response examples.

        Tests against endpoints: #36
        """
        response_files = [
            "36_get_link_template.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = LinkTemplate(**data)
                        self._validate_link_template_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"LinkTemplate validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LinkTemplate(**item)
                            self._validate_link_template_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"LinkTemplate validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = LinkTemplate(**data)
                    self._validate_link_template_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"LinkTemplate validation failed for {filename}: {e}")

    def _validate_link_template_fields(self, model: LinkTemplate, original_data: dict):
        """Validate specific fields for LinkTemplate."""
        # Add model-specific field validations here
        assert hasattr(model, "label"), "Missing required field: label"
        assert hasattr(model, "linkType"), "Missing required field: linkType"
        assert hasattr(model, "active"), "Missing required field: active"

    def test_workzone_validation(self, response_examples_path):
        """Validate Workzone model against saved response examples.

        Tests against endpoints: #82
        """
        response_files = [
            "82_get_workzone.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = Workzone(**data)
                        self._validate_workzone_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Workzone validation failed for {filename}: {e}")

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workzone(**item)
                            self._validate_workzone_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"Workzone validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = Workzone(**data)
                    self._validate_workzone_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Workzone validation failed for {filename}: {e}")

    def _validate_workzone_fields(self, model: Workzone, original_data: dict):
        """Validate specific fields for Workzone."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_validation(self, response_examples_path):
        """Validate ActivityType model against saved response examples.

        Tests against endpoints: #5
        """
        response_files = [
            "5_get_activityTypes_11_11.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = ActivityType(**data)
                        self._validate_activity_type_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ActivityType validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityType(**item)
                            self._validate_activity_type_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ActivityType validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ActivityType(**data)
                    self._validate_activity_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityType validation failed for {filename}: {e}")

    def _validate_activity_type_fields(self, model: ActivityType, original_data: dict):
        """Validate specific fields for ActivityType."""
        # Add model-specific field validations here
        assert hasattr(model, "label"), "Missing required field: label"
        assert hasattr(model, "name"), "Missing required field: name"
        assert hasattr(model, "active"), "Missing required field: active"

    def test_routing_plan_list_response_validation(self, response_examples_path):
        """Validate RoutingPlanListResponse model against saved response examples.

        Tests against endpoints: #58
        """
        response_files = [
            "58_get_routingProfiles_MaintenanceRoutingProfile_plans_MaintenanceRoutingProfile.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = RoutingPlanListResponse(**data)
                        self._validate_routing_plan_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"RoutingPlanListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingPlan(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with RoutingPlan"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"RoutingPlan validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingPlanListResponse(**item)
                            self._validate_routing_plan_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"RoutingPlanListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = RoutingPlanListResponse(**data)
                    self._validate_routing_plan_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"RoutingPlanListResponse validation failed for {filename}: {e}"
                    )

    def _validate_routing_plan_list_response_fields(
        self, model: RoutingPlanListResponse, original_data: dict
    ):
        """Validate specific fields for RoutingPlanListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_application_api_access_validation(self, response_examples_path):
        """Validate ApplicationApiAccess model against saved response examples.

        Tests against endpoints: #11
        """
        response_files = [
            "11_get_applications_demoauth_apiAccess_metadataAPI_demoauth_metadataAPI.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationApiAccess(**data)
                        self._validate_application_api_access_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"ApplicationApiAccess validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationApiAccess(**item)
                            self._validate_application_api_access_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"ApplicationApiAccess validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = ApplicationApiAccess(**data)
                    self._validate_application_api_access_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"ApplicationApiAccess validation failed for {filename}: {e}"
                    )

    def _validate_application_api_access_fields(
        self, model: ApplicationApiAccess, original_data: dict
    ):
        """Validate specific fields for ApplicationApiAccess."""
        # Add model-specific field validations here
        if hasattr(model, "status") and getattr(model, "status") is not None:
            assert getattr(model, "status") in ["active", "inactive"], (
                "Invalid enum value for status"
            )

    def test_inventory_type_list_response_validation(self, response_examples_path):
        """Validate InventoryTypeListResponse model against saved response examples.

        Tests against endpoints: #31
        """
        response_files = [
            "31_get_inventory_types.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = InventoryTypeListResponse(**data)
                        self._validate_inventory_type_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"InventoryTypeListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = InventoryType(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with InventoryType"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"InventoryType validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = InventoryTypeListResponse(**item)
                            self._validate_inventory_type_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"InventoryTypeListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = InventoryTypeListResponse(**data)
                    self._validate_inventory_type_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"InventoryTypeListResponse validation failed for {filename}: {e}"
                    )

    def _validate_inventory_type_list_response_fields(
        self, model: InventoryTypeListResponse, original_data: dict
    ):
        """Validate specific fields for InventoryTypeListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )

    def test_property_response_validation(self, response_examples_path):
        """Validate PropertyResponse model against saved response examples.

        Tests against endpoints: #51
        """
        response_files = [
            "51_property.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = PropertyResponse(**data)
                        self._validate_property_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"PropertyResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = PropertyResponse(**item)
                            self._validate_property_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"PropertyResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = PropertyResponse(**data)
                    self._validate_property_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"PropertyResponse validation failed for {filename}: {e}"
                    )

    def _validate_property_response_fields(
        self, model: PropertyResponse, original_data: dict
    ):
        """Validate specific fields for PropertyResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_organization_list_response_validation(self, response_examples_path):
        """Validate OrganizationListResponse model against saved response examples.

        Tests against endpoints: #46
        """
        response_files = [
            "46_get_organizations.json",
        ]

        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue

            with open(file_path) as f:
                data = json.load(f)

            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]

            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = OrganizationListResponse(**data)
                        self._validate_organization_list_response_fields(
                            model_instance, data
                        )
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(
                            f"OrganizationListResponse validation failed for {filename}: {e}"
                        )

                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Organization(**item)
                            print(
                                f"✅ Validated {filename} item {idx} with Organization"
                            )
                        except ValidationError as e:
                            pytest.fail(
                                f"Organization validation failed for {filename} item {idx}: {e}"
                            )
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = OrganizationListResponse(**item)
                            self._validate_organization_list_response_fields(
                                model_instance, item
                            )
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(
                                f"OrganizationListResponse validation failed for {filename} item {idx}: {e}"
                            )
            else:
                # Validate single response
                try:
                    model_instance = OrganizationListResponse(**data)
                    self._validate_organization_list_response_fields(
                        model_instance, data
                    )
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(
                        f"OrganizationListResponse validation failed for {filename}: {e}"
                    )

    def _validate_organization_list_response_fields(
        self, model: OrganizationListResponse, original_data: dict
    ):
        """Validate specific fields for OrganizationListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, "items"), "List response should have 'items' field"
        assert hasattr(model, "totalResults"), (
            "List response should have 'totalResults' field"
        )
