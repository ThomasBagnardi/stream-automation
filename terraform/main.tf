# ==========================================
# 1. THE SETTINGS BLOCK
# ==========================================
terraform {
    required_version = ">= 1.5.0"

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

# ==========================================
# 2. THE PROVIDER CONFIGURATION BLOCK
# ==========================================
provider "aws" {
    region = "us-east-1"
    access_key = "mock_access_key"
    secret_key = "mock_secret_key"
    skip_credentials_validation = true
    skip_metadata_api_check = true
    skip_requesting_account_id = true
    s3_use_path_style = true

    # Redirect standard AWS API requests to local LocalStack container
    endpoints {
        s3 = "http://localhost:4566"
    }
}

# ==========================================
# 3. THE COMPONENT RESOURCE BLOCK
# ==========================================
resource "aws_s3_bucket" "stream_storage" {
    bucket = "automated-stream-payloads"
    force_destroy = true # Allows clean teardown during testing
}