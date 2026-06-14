import boto3

# Tell boto3 to talk to offline LocalStack cloud instead of real AWS
s3 = boto3.client("s3", endpoint_url="http://localhost:4566")

# Create virtual storage bucket
s3.create_bucket(Bucket="stream-schedule-bucket")

# List buckets to prove it worked
response = s3.list_buckets()

print("[SUCCESS] Connected to LocaklStack!")
print("Your virtual cloud storage buckets:")
for bucket in response["Buckets"]:
    print(f" └── 📦 {bucket['Name']}")
