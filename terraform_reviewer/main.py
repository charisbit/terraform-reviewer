import os
import sys
from .reviewer import review_terraform_changes


def main():
    aws_region = os.getenv("AWS_REGION", "ap-northeast-1")
    model_id = os.getenv("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # Check if a filename was passed as a command-line argument
    if len(sys.argv) > 1:
        plan_file = sys.argv[1]
    else:
        plan_file = "plan.txt"

    # Read terraform plan
    try:
        with open(plan_file, "r") as f:
            plan_content = f.read()
    except FileNotFoundError:
        print(f"Error: Plan file {plan_file} not found.")
        sys.exit(1)

    # Review and comment on PR
    review_result = review_terraform_changes(
        plan_content=plan_content,
        aws_region=aws_region,
        model_id=model_id,
        github_token=github_token,
    )

    print(review_result)


if __name__ == "__main__":
    main()
