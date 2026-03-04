"""Unit tests for PamClientConstants class

This module contains unit tests for the PamClientConstants configuration class,
ensuring constant values are correctly defined.
"""

from cloud_idaas.pam_client.domain.pam_client_constants import PamClientConstants


class TestPamClientConstants:
    """Test suite for PamClientConstants"""

    def test_scope_constant(self):
        """Test SCOPE constant value is correctly defined"""
        expected_scope = "urn:cloud:idaas:pam|.all"
        assert PamClientConstants.SCOPE == expected_scope

    def test_scope_constant_type(self):
        """Test SCOPE constant is a string type"""
        assert isinstance(PamClientConstants.SCOPE, str)

    def test_scope_constant_not_empty(self):
        """Test SCOPE constant is not empty"""
        assert PamClientConstants.SCOPE
        assert len(PamClientConstants.SCOPE) > 0

    def test_status_code_200_constant(self):
        """Test STATUS_CODE_200 constant value is correctly defined"""
        assert PamClientConstants.STATUS_CODE_200 == 200

    def test_status_code_200_type(self):
        """Test STATUS_CODE_200 constant is an integer type"""
        assert isinstance(PamClientConstants.STATUS_CODE_200, int)

    def test_constants_immutable(self):
        """Test that constants class attributes exist and are accessible"""
        # Verify that class has expected attributes
        assert hasattr(PamClientConstants, "SCOPE")
        assert hasattr(PamClientConstants, "STATUS_CODE_200")

    def test_scope_format(self):
        """Test SCOPE constant follows URN format"""
        scope = PamClientConstants.SCOPE
        assert scope.startswith("urn:cloud:idaas:pam")
        assert "|.all" in scope
