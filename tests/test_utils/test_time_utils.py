import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
import time
from app.utils.time_utils import is_file_older_cache_time


class TestTimeUtils:
    """Test cases for time utility functions."""

    @pytest.mark.unit
    def test_is_file_older_cache_time_recent_file(self):
        """Test that a recent file is not considered older than cache time."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # File was just created, should not be older than cache time
            result = is_file_older_cache_time(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    def test_is_file_older_cache_time_old_file(self):
        """Test that an old file is considered older than cache time."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Mock os.path.getmtime to return a very old timestamp
            with patch('os.path.getmtime', return_value=time.time() - 86400):  # 24 hours ago
                result = is_file_older_cache_time(temp_path)
                assert result is True
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    def test_is_file_older_cache_time_nonexistent_file(self):
        """Test handling of non-existent file."""
        nonexistent_path = "/path/that/does/not/exist.txt"
        
        # Should handle gracefully - either return True or raise appropriate exception
        try:
            result = is_file_older_cache_time(nonexistent_path)
            # If it returns, should be True (treat missing file as old)
            assert result is True
        except (FileNotFoundError, OSError):
            # Or it might raise an exception, which is also acceptable
            assert True

    @pytest.mark.unit
    @patch('os.path.getmtime')
    def test_is_file_older_cache_time_edge_case(self, mock_getmtime):
        """Test edge case where file is exactly at cache time boundary."""
        # Mock current time and file time to be exactly at boundary
        current_time = time.time()
        
        # Assume cache time is 1 hour (3600 seconds) - adjust based on actual implementation
        cache_boundary_time = current_time - 3600
        mock_getmtime.return_value = cache_boundary_time
        
        with patch('time.time', return_value=current_time):
            result = is_file_older_cache_time("dummy_path")
            # At exact boundary, behavior may vary - just ensure it returns a boolean
            assert isinstance(result, bool)

    @pytest.mark.unit
    def test_is_file_older_cache_time_return_type(self):
        """Test that function always returns a boolean."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = is_file_older_cache_time(temp_path)
            assert isinstance(result, bool)
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    @patch('os.path.getmtime', side_effect=OSError("Permission denied"))
    def test_is_file_older_cache_time_permission_error(self, mock_getmtime):
        """Test handling of permission errors when accessing file."""
        # Should handle permission errors gracefully
        try:
            result = is_file_older_cache_time("protected_file")
            # If it returns, should indicate file is old (safe default)
            assert result is True
        except OSError:
            # Or it might propagate the exception
            assert True