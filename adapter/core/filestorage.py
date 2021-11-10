import os

import boto3


class Filestorage:
    def _get_link(self):
        num = random.random() * len(self.ptr_addresses)
        return ""

    def _upload_directory(path):
        session = boto3.Session(
            aws_access_key_id="AWS_ACCESS_KEY_ID",
            aws_secret_access_key="AWS_SECRET_ACCESS_KEY_ID",
            region_name="AWS_ACCOUNT_REGION",
        )
        s3 = session.resource("s3")
        bucket = s3.Bucket("S3_BUCKET_NAME")

        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, "rb") as data:
                    bucket.put_object(Key=full_path[len(path) + 1 :], Body=data)
