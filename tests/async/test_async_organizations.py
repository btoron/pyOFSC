"""Async tests for organization operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import Organization, OrganizationListResponse, OrganizationType


class TestAsyncGetOrganizationsLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_organizations(self, async_instance: AsyncOFSC):
        """Test get_organizations with actual API - validates structure"""
        organizations = await async_instance.metadata.get_organizations()

        # Verify type validation
        assert isinstance(organizations, OrganizationListResponse)
        assert organizations.totalResults is not None
        assert organizations.totalResults >= 0
        assert hasattr(organizations, "items")
        assert isinstance(organizations.items, list)

        # Verify at least one organization exists
        if len(organizations.items) > 0:
            assert isinstance(organizations.items[0], Organization)


class TestAsyncGetOrganizations:
    """Test async get_organizations method."""

    @pytest.mark.asyncio
    async def test_get_organizations_with_model(self, async_instance: AsyncOFSC):
        """Test that get_organizations returns OrganizationListResponse model"""
        organizations = await async_instance.metadata.get_organizations()

        # Verify type validation
        assert isinstance(organizations, OrganizationListResponse)
        assert hasattr(organizations, "items")
        assert hasattr(organizations, "totalResults")
        assert isinstance(organizations.items, list)

        # Verify items are Organization instances
        if len(organizations.items) > 0:
            assert isinstance(organizations.items[0], Organization)
            assert hasattr(organizations.items[0], "label")
            assert hasattr(organizations.items[0], "name")
            assert hasattr(organizations.items[0], "type")
            assert hasattr(organizations.items[0], "translations")

    @pytest.mark.asyncio
    async def test_get_organizations_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        organizations = await async_instance.metadata.get_organizations()
        assert organizations.totalResults is not None
        assert isinstance(organizations.totalResults, int)
        assert organizations.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_organizations_field_types(self, async_instance: AsyncOFSC):
        """Test that organization fields have correct types"""
        organizations = await async_instance.metadata.get_organizations()

        if len(organizations.items) > 0:
            organization = organizations.items[0]
            assert isinstance(organization.label, str)
            assert isinstance(organization.name, str)
            assert isinstance(organization.type, OrganizationType)
            assert organization.type in [
                OrganizationType.contractor,
                OrganizationType.inhouse,
            ]


class TestAsyncGetOrganization:
    """Test async get_organization method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_organization(self, async_instance: AsyncOFSC):
        """Test get_organization with actual API"""
        # Get list of organizations first to find a valid one
        organizations = await async_instance.metadata.get_organizations()
        assert len(organizations.items) > 0

        # Get the first organization by label
        first_label = organizations.items[0].label
        organization = await async_instance.metadata.get_organization(first_label)

        # Verify type validation
        assert isinstance(organization, Organization)
        assert organization.label == first_label
        assert isinstance(organization.name, str)
        assert isinstance(organization.type, OrganizationType)
        assert organization.type in [
            OrganizationType.contractor,
            OrganizationType.inhouse,
        ]

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_organization_not_found(self, async_instance: AsyncOFSC):
        """Test get_organization with non-existent organization"""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_organization("NONEXISTENT_ORG_12345")


class TestAsyncOrganizationSavedResponses:
    """Test model validation against saved API responses."""

    def test_organization_list_response_validation(self):
        """Test OrganizationListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "organizations"
            / "get_organizations_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = OrganizationListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, OrganizationListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, Organization) for item in response.items)

        # Verify first organization details
        first_org = response.items[0]
        assert isinstance(first_org, Organization)
        assert first_org.label == "default"
        assert first_org.name == "Supremo Power Organization"
        assert first_org.type == OrganizationType.inhouse

    def test_organization_single_response_validation(self):
        """Test Organization model validates against saved single response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "organizations"
            / "get_organization_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        organization = Organization.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(organization, Organization)
        assert organization.label == "default"
        assert organization.name == "Supremo Power Organization"
        assert organization.type == OrganizationType.inhouse
        assert isinstance(organization.type, OrganizationType)
