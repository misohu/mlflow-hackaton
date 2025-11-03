# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
from charmed_kubeflow_chisme.exceptions import ErrorWithStatus
from ops.model import BlockedStatus, WaitingStatus
from ops.testing import Harness

from charm import MlflowCharm


@pytest.fixture(scope="function")
def harness() -> Harness:
    """Create and return Harness for testing."""
    harness = Harness(MlflowCharm)
    harness.set_can_connect("mlflow-server", True)
    return harness


class TestConfigValidation:
    """Test class for configuration validation."""

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_success(self, harness: Harness):
        """Test config validation with valid config."""
        harness.begin()
        # Should not raise any exception
        harness.charm._validate_config()

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_mlflow_port_too_low(self, harness: Harness):
        """Test config validation with port number too low."""
        harness.update_config({"mlflow_port": 1023})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid mlflow_port: 1023" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_mlflow_port_too_high(self, harness: Harness):
        """Test config validation with port number too high."""
        harness.update_config({"mlflow_port": 65536})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid mlflow_port: 65536" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_exporter_port(self, harness: Harness):
        """Test config validation with invalid exporter port."""
        harness.update_config({"mlflow_prometheus_exporter_port": 100})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid mlflow_prometheus_exporter_port: 100" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_nodeport(self, harness: Harness):
        """Test config validation with invalid nodeport."""
        harness.update_config({"mlflow_nodeport": 70000})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid mlflow_nodeport: 70000" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_exporter_nodeport(self, harness: Harness):
        """Test config validation with invalid exporter nodeport."""
        harness.update_config({"mlflow_prometheus_exporter_nodeport": 500})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid mlflow_prometheus_exporter_nodeport: 500" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_nodeport_conflict(self, harness: Harness):
        """Test config validation with conflicting nodeports."""
        harness.update_config(
            {
                "enable_mlflow_nodeport": True,
                "mlflow_nodeport": 31380,
                "mlflow_prometheus_exporter_nodeport": 31380,
            }
        )
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "NodePort conflict" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_invalid_bucket_name(self, harness: Harness):
        """Test config validation with invalid S3 bucket name."""
        harness.update_config({"default_artifact_root": "Invalid_Bucket_Name!"})
        harness.begin()
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_config()
        assert "Invalid default_artifact_root" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_config_valid_bucket_name(self, harness: Harness):
        """Test config validation with valid S3 bucket name."""
        harness.update_config({"default_artifact_root": "my-valid-bucket-123"})
        harness.begin()
        # Should not raise any exception
        harness.charm._validate_config()


class TestDatabaseValidation:
    """Test class for database relation data validation."""

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_success(self, harness: Harness):
        """Test database validation with valid data."""
        harness.begin()
        db_data = {
            "host": "mysql.example.com",
            "port": "3306",
            "username": "mlflow",
            "password": "secret123",
        }
        # Should not raise any exception
        harness.charm._validate_database_data(db_data)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_missing_host(self, harness: Harness):
        """Test database validation with missing host."""
        harness.begin()
        db_data = {
            "port": "3306",
            "username": "mlflow",
            "password": "secret123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_database_data(db_data)
        assert "Missing or empty required database field: host" in str(exc_info.value)
        assert exc_info.value.status_type(WaitingStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_empty_username(self, harness: Harness):
        """Test database validation with empty username."""
        harness.begin()
        db_data = {
            "host": "mysql.example.com",
            "port": "3306",
            "username": "",
            "password": "secret123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_database_data(db_data)
        assert "Missing or empty required database field: username" in str(exc_info.value)
        assert exc_info.value.status_type(WaitingStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_invalid_port_non_numeric(self, harness: Harness):
        """Test database validation with non-numeric port."""
        harness.begin()
        db_data = {
            "host": "mysql.example.com",
            "port": "not-a-port",
            "username": "mlflow",
            "password": "secret123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_database_data(db_data)
        assert "Invalid database port" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_invalid_port_out_of_range(self, harness: Harness):
        """Test database validation with port out of range."""
        harness.begin()
        db_data = {
            "host": "mysql.example.com",
            "port": "70000",
            "username": "mlflow",
            "password": "secret123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_database_data(db_data)
        assert "Invalid database port" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_database_data_invalid_host(self, harness: Harness):
        """Test database validation with invalid hostname."""
        harness.begin()
        db_data = {
            "host": "mysql@invalid!host",
            "port": "3306",
            "username": "mlflow",
            "password": "secret123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_database_data(db_data)
        assert "Invalid database host" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)


class TestObjectStorageValidation:
    """Test class for object storage relation data validation."""

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_success(self, harness: Harness):
        """Test object storage validation with valid data."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
            "secure": True,
        }
        # Should not raise any exception
        harness.charm._validate_object_storage_data(storage_data)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_missing_service(self, harness: Harness):
        """Test object storage validation with missing service."""
        harness.begin()
        storage_data = {
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Missing or empty required object storage field: service" in str(exc_info.value)
        assert exc_info.value.status_type(WaitingStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_empty_access_key(self, harness: Harness):
        """Test object storage validation with empty access key."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": 9000,
            "access-key": "",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Missing or empty required object storage field: access-key" in str(exc_info.value)
        assert exc_info.value.status_type(WaitingStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_invalid_port_non_numeric(self, harness: Harness):
        """Test object storage validation with non-numeric port."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": "not-a-port",
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Invalid object storage port" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_invalid_port_out_of_range(self, harness: Harness):
        """Test object storage validation with port out of range."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": 0,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Invalid object storage port" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_invalid_secure_field(self, harness: Harness):
        """Test object storage validation with invalid secure field."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
            "secure": "yes",  # Should be boolean
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Invalid 'secure' field" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_secure_field_optional(self, harness: Harness):
        """Test object storage validation with missing secure field (optional)."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
            # secure is optional
        }
        # Should not raise any exception
        harness.charm._validate_object_storage_data(storage_data)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_invalid_service_name(self, harness: Harness):
        """Test object storage validation with invalid service name."""
        harness.begin()
        storage_data = {
            "service": "minio@invalid!",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Invalid object storage service name" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_invalid_namespace(self, harness: Harness):
        """Test object storage validation with invalid namespace."""
        harness.begin()
        storage_data = {
            "service": "minio",
            "namespace": "invalid@namespace!",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        with pytest.raises(ErrorWithStatus) as exc_info:
            harness.charm._validate_object_storage_data(storage_data)
        assert "Invalid object storage namespace" in str(exc_info.value)
        assert exc_info.value.status_type(BlockedStatus)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_validate_object_storage_data_valid_service_and_namespace(self, harness: Harness):
        """Test object storage validation with valid service and namespace."""
        harness.begin()
        storage_data = {
            "service": "minio-service",
            "namespace": "my-namespace",
            "port": 9000,
            "access-key": "minioadmin",
            "secret-key": "minioadmin123",
        }
        # Should not raise any exception
        harness.charm._validate_object_storage_data(storage_data)


class TestInputSanitization:
    """Test class for input sanitization."""

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_sanitize_for_url_success(self, harness: Harness):
        """Test URL sanitization with valid input."""
        harness.begin()
        result = harness.charm._sanitize_for_url("my-service.namespace")
        assert result == "my-service.namespace"

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_sanitize_for_url_removes_special_chars(self, harness: Harness):
        """Test URL sanitization removes special characters."""
        harness.begin()
        result = harness.charm._sanitize_for_url("my@service#test")
        assert result == "myservicetest"

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_sanitize_for_url_non_string_input(self, harness: Harness):
        """Test URL sanitization with non-string input."""
        harness.begin()
        with pytest.raises(ValueError) as exc_info:
            harness.charm._sanitize_for_url(12345)
        assert "Expected string" in str(exc_info.value)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_sanitize_for_url_empty_after_sanitization(self, harness: Harness):
        """Test URL sanitization when result is empty."""
        harness.begin()
        with pytest.raises(ValueError) as exc_info:
            harness.charm._sanitize_for_url("@#$%")
        assert "Value became empty after sanitization" in str(exc_info.value)

    @patch(
        "charm.KubernetesServicePatch",
        lambda x, y, service_name, service_type, refresh_event: None,
    )
    def test_sanitize_for_url_preserves_safe_chars(self, harness: Harness):
        """Test URL sanitization preserves alphanumeric, hyphens, and dots."""
        harness.begin()
        result = harness.charm._sanitize_for_url("my-service_123.test")
        assert result == "my-service_123.test"
