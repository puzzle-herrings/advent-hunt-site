from hashlib import md5
from pathlib import Path

from cloudpathlib import S3Client
from environs import Env
import typer
from xxhash import xxh32

env = Env()
env.read_env()

UPLOAD_EXTRA_ARGS = {
    "CacheControl": "public, max-age=31536000",
}


def main(input_file: Path, dryrun: bool = False):
    content = input_file.read_bytes()
    md5sum = md5(content)
    xxh32sum = xxh32(content)
    print("md5sum: ", md5sum.hexdigest())
    print("xxh32sum: ", xxh32sum.hexdigest())

    if not dryrun:
        client = S3Client(endpoint_url=env("R2_ENDPOINT_URL"), extra_args=UPLOAD_EXTRA_ARGS)
        output_path = client.S3Path(f"s3://{env('R2_BUCKET_NAME')}/icons/{input_file.name}")
        output_path.upload_from(input_file, force_overwrite_to_cloud=True)
        print("Successfully uploaded to:", output_path)


if __name__ == "__main__":
    typer.run(main)
