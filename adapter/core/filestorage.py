from logging import log
import os, re

import boto3
from shared.core.log import Log
log = Log("DEBUG")
class FileStorage:
    def __init__(self, config):
        self.config = config

    def s3_upload_directory(self, path: str, testId):
        # TODO: ENV + CONFIGS?! Need to discuss
        aws_access_key_id = os.getenv(
            'AWS_ACCESS_KEY_ID', self.config["fileStorage"]["s3"]["awsAccessKeyId"])
        aws_secret_access_key = os.getenv(
            'AWS_SECRET_ACCESS_KEY', self.config["fileStorage"]["s3"]["awsSecretAccessKey"])
        region_name = os.getenv(
            'AWS_REGION', self.config["fileStorage"]["s3"]["regionName"])
        bucket_name = os.getenv(
            'AWS_S3_BUCKET', self.config["fileStorage"]["s3"]["bucketName"])

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        s3 = session.resource("s3")
        bucket = s3.Bucket(bucket_name)

        # TODO Add try except
        log.debug(f"Try upload allure result {testId} to s3")
        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                if re.search(r'target\/allure-results', full_path):
                    continue
                s3_directory = str(testId) + "/" + full_path[len(path) + 1:]
                with open(full_path, "rb") as data:
                    bucket.put_object(Key=s3_directory, Body=data)
        log.debug(f"Upload result {testId} to s3 finished")

    def run_selected_method(self, fsType: str, *args, **kwargs):
        do = f"{fsType}_upload_directory"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            func(*args, **kwargs)

    def upload_directory(self, path, testId):
        self.run_selected_method(
            self.config["fileStorage"]["type"], path, testId)
