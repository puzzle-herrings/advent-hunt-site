from hashlib import md5
from pathlib import Path, PurePosixPath
from typing import Annotated

from cloudpathlib import S3Client
from environs import Env
import typer
from xxhash import xxh32

env = Env()
env.read_env()

UPLOAD_EXTRA_ARGS = {
    "CacheControl": "public, max-age=31536000",
}


def main(
    input_file: Path,
    output_path: str,
    skip_confirmation: Annotated[bool, typer.Option("-y")] = False,
    dryrun: bool = False,
):
    output_path = PurePosixPath(output_path)
    assert not output_path.is_absolute(), "output_path must be a relative path"

    content = input_file.read_bytes()
    md5sum = md5(content)
    xxh32sum = xxh32(content)
    print("md5sum: ", md5sum.hexdigest())
    print("xxh32sum: ", xxh32sum.hexdigest())

    if not skip_confirmation:
        upload_path = f"s3://{env('R2_BUCKET_NAME')}/{output_path}"
        print("Uploading to:", upload_path)
        typer.confirm("Confirm?", abort=True)

    if not dryrun:
        client = S3Client(endpoint_url=env("R2_ENDPOINT_URL"), extra_args=UPLOAD_EXTRA_ARGS)
        cloud_path = client.S3Path(upload_path)
        cloud_path.upload_from(input_file, force_overwrite_to_cloud=True)
        print("Successfully uploaded to:", cloud_path)


if __name__ == "__main__":
    typer.run(main)
