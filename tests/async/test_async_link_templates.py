"""Async tests for link template operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    LinkTemplate,
    LinkTemplateAssignmentConstraint,
    LinkTemplateInterval,
    LinkTemplateListResponse,
    LinkTemplateSchedulingConstraint,
    LinkTemplateType,
)


class TestAsyncGetLinkTemplatesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_link_templates(self, async_instance: AsyncOFSC):
        """Test get_link_templates with actual API - validates structure"""
        link_templates = await async_instance.metadata.get_link_templates()

        # Verify type validation
        assert isinstance(link_templates, LinkTemplateListResponse)
        assert link_templates.totalResults is not None
        assert link_templates.totalResults >= 0
        assert hasattr(link_templates, "items")
        assert isinstance(link_templates.items, list)

        # Verify at least one link template exists
        if len(link_templates.items) > 0:
            assert isinstance(link_templates.items[0], LinkTemplate)


class TestAsyncGetLinkTemplates:
    """Test async get_link_templates method."""

    @pytest.mark.asyncio
    async def test_get_link_templates_with_model(self, async_instance: AsyncOFSC):
        """Test that get_link_templates returns LinkTemplateListResponse model"""
        link_templates = await async_instance.metadata.get_link_templates()

        # Verify type validation
        assert isinstance(link_templates, LinkTemplateListResponse)
        assert hasattr(link_templates, "items")
        assert hasattr(link_templates, "totalResults")
        assert isinstance(link_templates.items, list)

        # Verify items are LinkTemplate instances
        if len(link_templates.items) > 0:
            assert isinstance(link_templates.items[0], LinkTemplate)
            assert hasattr(link_templates.items[0], "label")
            assert hasattr(link_templates.items[0], "active")
            assert hasattr(link_templates.items[0], "linkType")
            assert hasattr(link_templates.items[0], "translations")

    @pytest.mark.asyncio
    async def test_get_link_templates_pagination(self, async_instance: AsyncOFSC):
        """Test get_link_templates with pagination"""
        link_templates = await async_instance.metadata.get_link_templates(
            offset=0, limit=2
        )
        assert isinstance(link_templates, LinkTemplateListResponse)
        assert link_templates.totalResults is not None

    @pytest.mark.asyncio
    async def test_get_link_templates_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        link_templates = await async_instance.metadata.get_link_templates()
        assert link_templates.totalResults is not None
        assert isinstance(link_templates.totalResults, int)
        assert link_templates.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_link_templates_field_types(self, async_instance: AsyncOFSC):
        """Test that link template fields have correct types"""
        link_templates = await async_instance.metadata.get_link_templates()

        if len(link_templates.items) > 0:
            link_template = link_templates.items[0]
            assert isinstance(link_template.label, str)
            assert isinstance(link_template.active, bool)
            assert isinstance(link_template.linkType, LinkTemplateType)
            assert link_template.linkType in [
                LinkTemplateType.finishToStart,
                LinkTemplateType.startToStart,
                LinkTemplateType.simultaneous,
                LinkTemplateType.related,
            ]
            assert isinstance(link_template.translations, list)
            # minInterval is optional
            if link_template.minInterval is not None:
                assert isinstance(link_template.minInterval, LinkTemplateInterval)
                assert link_template.minInterval in [
                    LinkTemplateInterval.unlimited,
                    LinkTemplateInterval.adjustable,
                    LinkTemplateInterval.nonAdjustable,
                ]
            # maxInterval is optional
            if link_template.maxInterval is not None:
                assert isinstance(link_template.maxInterval, LinkTemplateInterval)
                assert link_template.maxInterval in [
                    LinkTemplateInterval.unlimited,
                    LinkTemplateInterval.adjustable,
                    LinkTemplateInterval.nonAdjustable,
                ]
            # schedulingConstraint is optional
            if link_template.schedulingConstraint is not None:
                assert isinstance(
                    link_template.schedulingConstraint,
                    LinkTemplateSchedulingConstraint,
                )
                assert link_template.schedulingConstraint in [
                    LinkTemplateSchedulingConstraint.sameDay,
                    LinkTemplateSchedulingConstraint.differentDays,
                ]
            # assignmentConstraints is optional
            if link_template.assignmentConstraints is not None:
                assert isinstance(
                    link_template.assignmentConstraints,
                    LinkTemplateAssignmentConstraint,
                )
                assert link_template.assignmentConstraints in [
                    LinkTemplateAssignmentConstraint.sameResource,
                    LinkTemplateAssignmentConstraint.differentResources,
                ]


class TestAsyncGetLinkTemplate:
    """Test async get_link_template method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_link_template(self, async_instance: AsyncOFSC):
        """Test get_link_template with actual API"""
        # Get list of link templates first to find a valid one
        link_templates = await async_instance.metadata.get_link_templates()
        assert len(link_templates.items) > 0

        # Get the first link template by label
        first_label = link_templates.items[0].label
        link_template = await async_instance.metadata.get_link_template(first_label)

        # Verify type validation
        assert isinstance(link_template, LinkTemplate)
        assert link_template.label == first_label
        assert isinstance(link_template.active, bool)
        assert isinstance(link_template.linkType, LinkTemplateType)
        assert link_template.linkType in [
            LinkTemplateType.finishToStart,
            LinkTemplateType.startToStart,
            LinkTemplateType.simultaneous,
            LinkTemplateType.related,
        ]
        assert isinstance(link_template.translations, list)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_link_template_not_found(self, async_instance: AsyncOFSC):
        """Test get_link_template with non-existent link template"""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_link_template(
                "NONEXISTENT_TEMPLATE_12345"
            )


class TestAsyncLinkTemplateSavedResponses:
    """Test model validation against saved API responses."""

    def test_link_template_list_response_validation(self):
        """Test LinkTemplateListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "link_templates"
            / "get_link_templates_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = LinkTemplateListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, LinkTemplateListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, LinkTemplate) for item in response.items)

        # Verify first link template details
        first_template = response.items[0]
        assert isinstance(first_template, LinkTemplate)
        assert first_template.label == "starts_after"
        assert first_template.reverseLabel == "start_before"
        assert first_template.active is True
        assert first_template.linkType == LinkTemplateType.finishToStart
        assert isinstance(first_template.linkType, LinkTemplateType)

    def test_link_template_single_response_validation(self):
        """Test LinkTemplate model validates against saved single response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "link_templates"
            / "get_link_template_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        link_template = LinkTemplate.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(link_template, LinkTemplate)
        assert link_template.label == "starts_after"
        assert link_template.reverseLabel == "start_before"
        assert link_template.active is True
        assert link_template.linkType == LinkTemplateType.finishToStart
        assert isinstance(link_template.linkType, LinkTemplateType)
        assert link_template.minInterval == LinkTemplateInterval.nonAdjustable
        assert isinstance(link_template.minInterval, LinkTemplateInterval)
        assert link_template.maxInterval == LinkTemplateInterval.unlimited
        assert isinstance(link_template.maxInterval, LinkTemplateInterval)
        assert link_template.minIntervalValue == 0
        assert isinstance(link_template.translations, list)
        assert len(link_template.translations) > 0
