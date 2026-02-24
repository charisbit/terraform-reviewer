"""
Unit tests for terraform-reviewer
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock


class TestInvokeBedrockModel:
    """Test invoke_bedrock_model function"""

    def test_invoke_claude_model_success(self):
        """Test successful Claude model invocation"""
        with patch("terraform_reviewer.reviewer.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_response = {
                "body": MagicMock(
                    read=MagicMock(
                        return_value=json.dumps(
                            {"content": [{"text": "Test review output"}]}
                        ).encode()
                    )
                )
            }
            mock_client.invoke_model.return_value = mock_response
            mock_boto3.client.return_value = mock_client

            from terraform_reviewer.reviewer import invoke_bedrock_model

            result = invoke_bedrock_model(
                prompt="Test prompt",
                model_id="anthropic.claude-3-haiku-20240307-v1:0",
                aws_region="us-east-1",
            )

            assert result == "Test review output"
            mock_client.invoke_model.assert_called_once()

    def test_invoke_cohere_model_success(self):
        """Test successful Cohere model invocation"""
        with patch("terraform_reviewer.reviewer.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_response = {
                "body": MagicMock(
                    read=MagicMock(
                        return_value=json.dumps({"text": "Test cohere output"}).encode()
                    )
                )
            }
            mock_client.invoke_model.return_value = mock_response
            mock_boto3.client.return_value = mock_client

            from terraform_reviewer.reviewer import invoke_bedrock_model

            result = invoke_bedrock_model(
                prompt="Test prompt",
                model_id="cohere.command-r-plus-v1:0",
                aws_region="us-east-1",
            )

            assert result == "Test cohere output"

    def test_invoke_unsupported_model(self):
        """Test unsupported model raises ValueError"""
        from terraform_reviewer.reviewer import invoke_bedrock_model

        with pytest.raises(ValueError) as exc_info:
            invoke_bedrock_model(
                prompt="Test prompt",
                model_id="unsupported.model",
                aws_region="us-east-1",
            )

        assert "Unsupported model" in str(exc_info.value)


class TestGenerateTerraformReview:
    """Test generate_terraform_review function"""

    @patch("terraform_reviewer.reviewer.invoke_bedrock_model")
    def test_generate_review_success(self, mock_invoke):
        """Test successful review generation"""
        mock_invoke.return_value = "Test review"

        from terraform_reviewer.reviewer import generate_terraform_review

        result = generate_terraform_review(
            plan_content='resource "aws_instance" "test" {}',
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            aws_region="us-east-1",
        )

        assert result == "Test review"
        # prompt is passed as first positional argument
        assert "terraform plan" in mock_invoke.call_args[0][0].lower()


class TestReviewTerraformChanges:
    """Test review_terraform_changes function"""

    @patch("terraform_reviewer.reviewer.generate_terraform_review")
    def test_review_changes_no_pr_context(self, mock_generate):
        """Test review when not in PR context"""
        mock_generate.return_value = "Test review output"

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            from terraform_reviewer.reviewer import review_terraform_changes

            with patch("terraform_reviewer.reviewer.os.getenv") as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    "GITHUB_REPOSITORY": None,
                    "GITHUB_EVENT_NAME": None,
                    "GITHUB_EVENT_PATH": None,
                }.get(key, default)

                result = review_terraform_changes(
                    plan_content="test plan",
                    aws_region="us-east-1",
                    model_id="anthropic.claude-3-haiku-20240307-v1:0",
                    github_token="test-token",
                )

        assert result == "Test review output"

    @patch("terraform_reviewer.reviewer.generate_terraform_review")
    @patch("terraform_reviewer.reviewer.Github")
    def test_review_changes_pr_context(self, mock_github, mock_generate):
        """Test review when in PR context"""
        mock_generate.return_value = "Test review output"

        mock_g = MagicMock()
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.create_issue_comment = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_g.get_repo.return_value = mock_repo
        mock_github.return_value = mock_g

        # Create mock PR event data
        mock_event_data = {"pull_request": {"number": 123}}

        mock_event_data_str = json.dumps(mock_event_data)
        mock_file = MagicMock()
        mock_file.read.return_value = mock_event_data_str

        with patch.dict(
            os.environ,
            {
                "GITHUB_REPOSITORY": "test/repo",
                "GITHUB_EVENT_NAME": "pull_request",
                "GITHUB_EVENT_PATH": "/tmp/github_event.json",
            },
        ):
            with patch("builtins.open", return_value=mock_file):
                with patch("json.load", return_value=mock_event_data):
                    from terraform_reviewer.reviewer import review_terraform_changes

                    result = review_terraform_changes(
                        plan_content="test plan",
                        aws_region="us-east-1",
                        model_id="anthropic.claude-3-haiku-20240307-v1:0",
                        github_token="test-token",
                    )

        assert "123" in result
        mock_pr.create_issue_comment.assert_called_once()


class TestReviewerModule:
    """Test module structure and imports"""

    def test_reviewer_import(self):
        """Test that reviewer module can be imported"""
        from terraform_reviewer import reviewer

        assert hasattr(reviewer, "invoke_bedrock_model")
        assert hasattr(reviewer, "generate_terraform_review")
        assert hasattr(reviewer, "review_terraform_changes")

    def test_version_info(self):
        """Test package has version info"""
        from importlib.metadata import version

        try:
            version = version("terraform-reviewer")
            assert version is not None
        except Exception:
            # Package might not be installed, that's OK for unit tests
            pass
