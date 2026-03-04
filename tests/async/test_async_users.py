"""Async tests for user operations."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    CollaborationGroup,
    CollaborationGroupsResponse,
    User,
    UserCreate,
    UserListResponse,
)

SAVED_RESPONSES_DIR = Path(__file__).parent.parent / "saved_responses" / "users"

# Known test user login (used by live tests)
_TEST_USER_LOGIN = "claude_test_user_001"


@pytest.mark.uses_local_data
class TestAsyncUserSavedResponses:
    """Validate models against saved API response files."""

    def test_user_list_response_validation(self):
        """Test UserListResponse model validates against saved response."""
        with open(SAVED_RESPONSES_DIR / "get_users_200_success.json") as f:
            saved_data = json.load(f)

        response = UserListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, UserListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, User) for item in response.items)

        # Verify first user structure
        first = response.items[0]
        assert isinstance(first.login, str)
        assert isinstance(first.resources, list)

    def test_user_single_response_validation(self):
        """Test User model validates against saved single response."""
        with open(SAVED_RESPONSES_DIR / "get_user_200_success.json") as f:
            saved_data = json.load(f)

        # OFSC returns 'links' field that is not in our model — should be handled by extra="allow"
        user = User.model_validate(saved_data["response_data"])

        assert isinstance(user, User)
        assert isinstance(user.login, str)
        assert user.login == "demoauth"
        assert isinstance(user.name, str)
        assert isinstance(user.resources, list)
        assert isinstance(user.resourceInternalIds, list)

    def test_user_list_items_are_users(self):
        """Test that all items in list response are User instances."""
        with open(SAVED_RESPONSES_DIR / "get_users_200_success.json") as f:
            saved_data = json.load(f)

        response = UserListResponse.model_validate(saved_data["response_data"])
        for item in response.items:
            assert isinstance(item, User)
            assert isinstance(item.login, str)

    def test_user_extra_fields_allowed(self):
        """Test User model accepts unknown fields (extra='allow')."""
        data = {
            "login": "testuser",
            "name": "Test",
            "unknownField": "value",
            "anotherExtra": 123,
        }
        user = User.model_validate(data)
        assert user.login == "testuser"


class TestUserCreateModel:
    """Test UserCreate model enforces required fields."""

    def test_user_create_requires_name(self):
        """Test that UserCreate requires name."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "userType": "technician",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["BUCKET"],
                }
            )

    def test_user_create_requires_user_type(self):
        """Test that UserCreate requires userType."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "name": "Test User",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["BUCKET"],
                }
            )

    def test_user_create_requires_language(self):
        """Test that UserCreate requires language."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "name": "Test User",
                    "userType": "technician",
                    "timeZone": "US/Eastern",
                    "resources": ["BUCKET"],
                }
            )

    def test_user_create_requires_time_zone(self):
        """Test that UserCreate requires timeZone."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "name": "Test User",
                    "userType": "technician",
                    "language": "en",
                    "resources": ["BUCKET"],
                }
            )

    def test_user_create_requires_resources(self):
        """Test that UserCreate requires resources."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "name": "Test User",
                    "userType": "technician",
                    "language": "en",
                    "timeZone": "US/Eastern",
                }
            )

    def test_user_create_requires_password(self):
        """Test that UserCreate requires password."""
        with pytest.raises(Exception):
            UserCreate.model_validate(
                {
                    "name": "Test User",
                    "userType": "technician",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["BUCKET"],
                }
            )

    def test_user_create_valid(self):
        """Test UserCreate with all required fields."""
        uc = UserCreate.model_validate(
            {
                "name": "Test User",
                "userType": "technician",
                "language": "en",
                "timeZone": "US/Eastern",
                "resources": ["BUCKET"],
                "password": "ClaudeTest1!",
            }
        )
        assert uc.name == "Test User"
        assert uc.userType == "technician"
        assert uc.resources == ["BUCKET"]

    def test_user_create_with_optional_fields(self):
        """Test UserCreate with optional fields set."""
        uc = UserCreate.model_validate(
            {
                "name": "Test User",
                "userType": "technician",
                "language": "en",
                "timeZone": "US/Eastern",
                "resources": ["BUCKET"],
                "password": "secret123",
                "mainResourceId": "BUCKET",
                "selfAssignment": True,
            }
        )
        assert uc.password == "secret123"
        assert uc.mainResourceId == "BUCKET"
        assert uc.selfAssignment is True

    def test_user_create_model_dump_excludes_none(self):
        """Test that model_dump with exclude_none works correctly."""
        uc = UserCreate.model_validate(
            {
                "name": "Test User",
                "userType": "technician",
                "language": "en",
                "timeZone": "US/Eastern",
                "resources": ["BUCKET"],
                "password": "ClaudeTest1!",
            }
        )
        dumped = uc.model_dump(exclude_none=True)
        assert "name" in dumped
        assert "password" in dumped
        assert "mainResourceId" not in dumped

    def test_user_create_from_dict_in_create_user(self):
        """Test UserCreate validates from dict when passed to create_user."""
        data = {
            "name": "Test User",
            "userType": "technician",
            "language": "en",
            "timeZone": "US/Eastern",
            "resources": ["BUCKET"],
            "password": "ClaudeTest1!",
        }
        # Simulate what create_user does when given a dict
        uc = UserCreate.model_validate(data)
        body = uc.model_dump(exclude_none=True)
        assert body["name"] == "Test User"


class TestAsyncGetUsers:
    """Model validation tests for get_users (mocked)."""

    @pytest.mark.asyncio
    async def test_get_users_with_model(self, mock_instance: AsyncOFSC):
        """Test that get_users returns UserListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasMore": False,
            "totalResults": 2,
            "limit": 100,
            "offset": 0,
            "items": [
                {
                    "login": "user1",
                    "name": "User One",
                    "userType": "technician",
                    "status": "active",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["RES1"],
                    "resourceInternalIds": [101],
                },
                {
                    "login": "user2",
                    "name": "User Two",
                    "userType": "manager",
                    "status": "active",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["RES2"],
                    "resourceInternalIds": [102],
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_users()

        assert isinstance(result, UserListResponse)
        assert len(result.items) == 2
        assert all(isinstance(item, User) for item in result.items)
        assert result.items[0].login == "user1"
        assert result.items[1].login == "user2"

    @pytest.mark.asyncio
    async def test_get_users_pagination(self, mock_instance: AsyncOFSC):
        """Test get_users passes pagination params."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasMore": False,
            "totalResults": 5,
            "limit": 2,
            "offset": 2,
            "items": [
                {
                    "login": "user3",
                    "resources": [],
                    "resourceInternalIds": [],
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_users(offset=2, limit=2)

        assert isinstance(result, UserListResponse)
        assert len(result.items) == 1
        # Verify the mock was called with correct params
        call_kwargs = mock_instance.core._client.get.call_args
        assert call_kwargs.kwargs["params"] == {"offset": 2, "limit": 2}

    @pytest.mark.asyncio
    async def test_get_users_total_results(self, mock_instance: AsyncOFSC):
        """Test that totalResults is populated."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasMore": False,
            "totalResults": 42,
            "limit": 100,
            "offset": 0,
            "items": [],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_users()

        assert result.totalResults == 42
        assert isinstance(result.totalResults, int)

    @pytest.mark.asyncio
    async def test_get_users_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasMore": False,
            "totalResults": 1,
            "limit": 100,
            "offset": 0,
            "items": [
                {
                    "login": "testuser",
                    "name": "Test User",
                    "userType": "technician",
                    "status": "active",
                    "language": "en",
                    "timeZone": "US/Eastern",
                    "resources": ["RES1", "RES2"],
                    "resourceInternalIds": [1, 2],
                }
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_users()
        user = result.items[0]

        assert isinstance(user.login, str)
        assert isinstance(user.name, str)
        assert isinstance(user.userType, str)
        assert isinstance(user.resources, list)
        assert isinstance(user.resourceInternalIds, list)


class TestAsyncGetUser:
    """Model validation tests for get_user (mocked)."""

    @pytest.mark.asyncio
    async def test_get_user_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_user returns User model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "name": "Test User",
            "userType": "technician",
            "status": "active",
            "language": "en",
            "timeZone": "US/Eastern",
            "timeZoneIANA": "America/New_York",
            "resources": ["BUCKET"],
            "resourceInternalIds": [1],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_user("testuser")

        assert isinstance(result, User)
        assert result.login == "testuser"
        assert result.name == "Test User"
        assert result.userType == "technician"

    @pytest.mark.asyncio
    async def test_get_user_all_optional_fields(self, mock_instance: AsyncOFSC):
        """Test get_user handles all optional fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "fulluser",
            "name": "Full User",
            "userType": "administrator",
            "status": "active",
            "language": "en",
            "timeZone": "US/Pacific",
            "timeZoneIANA": "America/Los_Angeles",
            "mainResourceId": "MAIN_RES",
            "resources": ["MAIN_RES"],
            "resourceInternalIds": [99],
            "dateFormat": "mm/dd/yy",
            "longDateFormat": "mm/dd/yyyy",
            "timeFormat": "12-hour",
            "weekStart": "sunday",
            "selfAssignment": True,
            "passwordTemporary": False,
            "loginAttempts": 0,
            "links": [],
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_user("fulluser")

        assert isinstance(result, User)
        assert result.mainResourceId == "MAIN_RES"
        assert result.dateFormat == "mm/dd/yy"
        assert result.selfAssignment is True
        assert result.loginAttempts == 0


class TestAsyncGetUsersLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_users(self, async_instance: AsyncOFSC):
        """Test get_users with actual API - validates structure."""
        result = await async_instance.core.get_users(offset=0, limit=100)

        assert isinstance(result, UserListResponse)
        assert result.totalResults is not None
        assert result.totalResults >= 0
        assert isinstance(result.items, list)
        if len(result.items) > 0:
            assert isinstance(result.items[0], User)
            assert isinstance(result.items[0].login, str)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_users_pagination(self, async_instance: AsyncOFSC):
        """Test get_users pagination with real API."""
        page1 = await async_instance.core.get_users(offset=0, limit=1)
        assert isinstance(page1, UserListResponse)
        assert len(page1.items) <= 1


class TestAsyncGetUserLive:
    """Live tests for get_user."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_user_known(self, async_instance: AsyncOFSC):
        """Test get_user with a known user."""
        users = await async_instance.core.get_users(limit=1)
        if len(users.items) == 0:
            pytest.skip("No users available")
        login = users.items[0].login
        user = await async_instance.core.get_user(login)

        assert isinstance(user, User)
        assert user.login == login

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_user_not_found(self, async_instance: AsyncOFSC):
        """Test get_user with non-existent user raises OFSCNotFoundError."""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.core.get_user("NONEXISTENT_USER_12345")

        assert exc_info.value.status_code == 404


class TestAsyncCreateUpdateDeleteUser:
    """Live tests for CRUD operations."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_update_delete_user(self, async_instance: AsyncOFSC):
        """Test full lifecycle: create, update, delete user."""
        # 1. List users to find a resource we can use
        users = await async_instance.core.get_users(limit=1)
        if len(users.items) == 0:
            pytest.skip("No users available to derive a resource from")

        # Get a resource from an existing user
        sample_user = users.items[0]
        if not sample_user.resources:
            pytest.skip("No resources available on sample user")
        resource = sample_user.resources[0]

        # 2. Create user
        user_data = UserCreate.model_validate(
            {
                "name": "Claude Test User",
                "userType": "technician",
                "language": "en",
                "timeZone": "America/New_York",
                "resources": [resource],
                "password": "ClaudeTest1!",
            }
        )
        created = await async_instance.core.create_user(_TEST_USER_LOGIN, user_data)
        assert isinstance(created, User)
        assert created.login == _TEST_USER_LOGIN

        try:
            # 3. Update user
            updated = await async_instance.core.update_user(
                _TEST_USER_LOGIN, {"name": "Claude Test User Updated"}
            )
            assert isinstance(updated, User)
            assert updated.name == "Claude Test User Updated"

            # 4. Verify update
            fetched = await async_instance.core.get_user(_TEST_USER_LOGIN)
            assert fetched.name == "Claude Test User Updated"

        finally:
            # 5. Delete user (cleanup)
            await async_instance.core.delete_user(_TEST_USER_LOGIN)

        # 6. Verify deletion
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_user(_TEST_USER_LOGIN)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_user_from_dict(self, async_instance: AsyncOFSC):
        """Test create_user accepts dict input."""
        users = await async_instance.core.get_users(limit=1)
        if len(users.items) == 0 or not users.items[0].resources:
            pytest.skip("No users/resources available")

        resource = users.items[0].resources[0]
        login = f"{_TEST_USER_LOGIN}_dict"

        created = await async_instance.core.create_user(
            login,
            {
                "name": "Claude Dict Test User",
                "userType": "technician",
                "language": "en",
                "timeZone": "America/New_York",
                "resources": [resource],
                "password": "ClaudeTest1!",
            },
        )
        assert isinstance(created, User)

        # Cleanup
        await async_instance.core.delete_user(login)


class TestAsyncUserCollabGroups:
    """Mocked tests for collaboration group methods."""

    @pytest.mark.asyncio
    async def test_get_user_collab_groups_model(self, mock_instance: AsyncOFSC):
        """Test get_user_collab_groups returns CollaborationGroupsResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "Group A"},
                {"name": "Group B"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_user_collab_groups("testuser")

        assert isinstance(result, CollaborationGroupsResponse)
        assert len(result) == 2
        assert isinstance(result[0], CollaborationGroup)
        assert result[0].name == "Group A"

    @pytest.mark.asyncio
    async def test_set_user_collab_groups_model(self, mock_instance: AsyncOFSC):
        """Test set_user_collab_groups sends correct body and returns model."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "items": [
                {"name": "GroupX"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.set_user_collab_groups("testuser", ["GroupX"])

        assert isinstance(result, CollaborationGroupsResponse)
        assert result[0].name == "GroupX"

        # Verify body format
        call_kwargs = mock_instance.core._client.post.call_args
        assert call_kwargs.kwargs["json"] == {"items": [{"name": "GroupX"}]}

    @pytest.mark.asyncio
    async def test_delete_user_collab_groups_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_user_collab_groups returns None."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_user_collab_groups("testuser")

        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_user_collab_groups_live(self, async_instance: AsyncOFSC):
        """Test get_user_collab_groups with actual API."""
        users = await async_instance.core.get_users(limit=1)
        if len(users.items) == 0:
            pytest.skip("No users available")
        login = users.items[0].login
        result = await async_instance.core.get_user_collab_groups(login)

        assert isinstance(result, CollaborationGroupsResponse)
        assert isinstance(result.items, list)


class TestAsyncUserFileProperty:
    """Mocked tests for file property methods."""

    @pytest.mark.asyncio
    async def test_get_user_property_returns_bytes(self, mock_instance: AsyncOFSC):
        """Test get_user_property returns bytes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake_binary_data"
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.get_user_property("testuser", "photo")

        assert isinstance(result, bytes)
        assert result == b"fake_binary_data"

        # Verify Accept header was set to octet-stream
        call_kwargs = mock_instance.core._client.get.call_args
        assert call_kwargs.kwargs["headers"]["Accept"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_set_user_property_returns_none(self, mock_instance: AsyncOFSC):
        """Test set_user_property returns None on success (204)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.set_user_property(
            "testuser",
            "photo",
            b"image_data",
            "photo.jpg",
            "image/jpeg",
        )

        assert result is None

        # Verify correct headers
        call_kwargs = mock_instance.core._client.put.call_args
        headers = call_kwargs.kwargs["headers"]
        assert headers["Content-Type"] == "image/jpeg"
        assert 'filename="photo.jpg"' in headers["Content-Disposition"]

    @pytest.mark.asyncio
    async def test_delete_user_property_returns_none(self, mock_instance: AsyncOFSC):
        """Test delete_user_property returns None on success (204)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.delete_user_property("testuser", "photo")

        assert result is None


class TestAsyncUserExceptions:
    """Test exception handling for user methods."""

    @pytest.mark.asyncio
    async def test_get_user_not_found_mock(self, mock_instance: AsyncOFSC):
        """Test get_user raises OFSCNotFoundError for 404 response."""
        import httpx

        mock_request = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5",
            "title": "Not Found",
            "detail": "User not found",
        }
        mock_response.text = "User not found"

        http_error = httpx.HTTPStatusError(
            "404 Not Found", request=mock_request, response=mock_response
        )
        mock_response.raise_for_status = Mock(side_effect=http_error)
        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await mock_instance.core.get_user("nobody")

    @pytest.mark.asyncio
    async def test_create_user_invalid_data_raises_validation_error(self):
        """Test UserCreate rejects invalid data."""
        with pytest.raises(Exception):
            UserCreate.model_validate({"name": "Test"})  # Missing required fields
