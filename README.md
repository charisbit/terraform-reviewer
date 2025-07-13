# 🔍 Terraform Reviewer

Terraform Reviewer is a GitHub Action that automatically reviews Terraform changes in Pull Requests using Amazon Bedrock AI. It provides comprehensive security analysis, best practice recommendations, and cost impact assessments.


## ✨ Features

- 🤖 **AI-Powered Reviews**: Uses Amazon Bedrock with Claude 3 Haiku or Cohere Command R+ models
- 🛡️ **Security Analysis**: Comprehensive security assessments including IAM, encryption, and access control
- 💰 **Cost Impact**: Estimates cost changes and provides optimization recommendations
- 🔐 **OIDC Authentication**: Secure AWS access using OpenID Connect Federation
- 📊 **Best Practices**: Identifies violations and suggests improvements
- ⚡ **Fast**: Lightweight action that integrates seamlessly into your CI/CD pipeline

## 🚀 Quick Start

### Prerequisites

- AWS account with Amazon Bedrock access in Tokyo region (ap-northeast-1)
- IAM role configured for OIDC Federation
- Terraform configuration in your repository
- GitHub repository with Actions enabled

### Setup

1. **Configure AWS IAM Role for OIDC**
   - Create an IAM role for GitHub Actions OIDC
   - Grant necessary permissions for Amazon Bedrock access
   - Note the role ARN for workflow configuration

2. **Enable Amazon Bedrock Models**
   - In AWS Console, navigate to Amazon Bedrock
   - Enable access to Claude 3 Haiku or Cohere Command R+ models
   - Ensure the models are available in ap-northeast-1 region

3. **Add to Your Workflow**

```yaml
name: Terraform Review

on:
  pull_request:
    branches: [ main ]

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  terraform-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.5.0

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan -out=plan.out

      - name: Review Terraform Changes
        uses: your-org/terraform-reviewer@v1.0.0
        with:
          aws_region: ap-northeast-1
          aws_role_arn: arn:aws:iam::ACCOUNT-ID:role/GitHubActionsRole
          model_id: anthropic.claude-3-haiku-20240307-v1:0
          terraform_plan_file: plan.out
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## 📋 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `aws_region` | AWS region for Bedrock | ✅ Yes | `ap-northeast-1` |
| `aws_role_arn` | AWS IAM role ARN for OIDC authentication | ✅ Yes | - |
| `model_id` | Bedrock model ID (claude-3-haiku or cohere.command-r-plus) | ❌ No | `anthropic.claude-3-haiku-20240307-v1:0` |
| `terraform_plan_file` | Terraform plan file path | ❌ No | `plan.out` |
| `github_token` | GitHub token for PR operations | ✅ Yes | - |

## 🔧 Supported Models

- **Claude 3 Haiku**: `anthropic.claude-3-haiku-20240307-v1:0`
- **Cohere Command R+**: `cohere.command-r-plus-v1:0`




## 🔧 Troubleshooting

### Common Issues

**Issue**: "AWS credentials not configured"
- **Solution**: Ensure OIDC is properly configured and the IAM role has correct permissions
- **Tip**: Check the role trust policy includes your GitHub repository

**Issue**: "Bedrock model access denied"
- **Solution**: Enable the model in Amazon Bedrock console and ensure IAM permissions
- **Tip**: Models must be enabled in the same region specified in `aws_region`

**Issue**: "Plan file not found"
- **Solution**: Ensure the `terraform_plan_file` path is correct and the file exists
- **Tip**: Use `terraform plan -out=plan.out` to generate the binary plan file

**Issue**: "GitHub token permissions insufficient"
- **Solution**: Ensure the workflow has `pull-requests: write` permission
- **Tip**: The action needs to comment on PRs for reviews

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is proprietary software licensed for internal use only - see the [LICENSE](LICENSE) file for details.

## 🏷️ Versioning

We use [Semantic Versioning](http://semver.org/) for versioning.

---

Made with ❤️ by Sei I
