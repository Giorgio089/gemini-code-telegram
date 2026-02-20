import sys
import os
from unittest.mock import MagicMock

# Set environment variables for bot.py
os.environ["TELEGRAM_TOKEN"] = "fake_token"
os.environ["GEMINI_API_KEY"] = "fake_key"
os.environ["AUTHORIZED_USER_ID"] = "123456"

# Mocking external dependencies before importing bot.py
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["telegram"] = MagicMock()
sys.modules["telegram.ext"] = MagicMock()

import pytest
from unittest.mock import patch, mock_open

# Now we can import read_file
from bot import read_file

def test_read_file_success():
    """Test read_file with a valid file."""
    mock_content = "Hello, world!"
    with patch("builtins.open", mock_open(read_data=mock_content)):
        result = read_file("test.txt")
        assert result == mock_content

def test_read_file_exception():
    """Test read_file when an exception occurs during file reading."""
    error_message = "File not found"
    with patch("builtins.open", side_effect=Exception(error_message)):
        result = read_file("non_existent_file.txt")
        assert result == error_message

def test_read_file_permission_error():
    """Test read_file when a PermissionError occurs."""
    error_message = "Permission denied"
    with patch("builtins.open", side_effect=PermissionError(error_message)):
        result = read_file("protected_file.txt")
        assert result == error_message
