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


def main(input_file: Path, solution: bool = False, dryrun: bool = False):
    content = input_file.read_bytes()
    md5sum = md5(content)
    xxh32sum = xxh32(content)
    print("md5sum: ", md5sum.hexdigest())
    print("xxh32sum: ", xxh32sum.hexdigest())

    calendar_day: int = int(typer.prompt("Calendar day"))
    slug: str = typer.prompt("Slug")
    output_file_name = f"{calendar_day:02d}-{slug}-{xxh32sum.hexdigest()}.pdf"
    print("Output file name:", output_file_name)

    if not dryrun:
        client = S3Client(endpoint_url=env("R2_ENDPOINT_URL"), extra_args=UPLOAD_EXTRA_ARGS)
        if not solution:
            output_path = client.S3Path(f"s3://{env('R2_BUCKET_NAME')}/puzzles/{output_file_name}")
        else:
            output_path = client.S3Path(
                f"s3://{env('R2_BUCKET_NAME')}/solutions/{output_file_name}"
            )
        output_path.upload_from(input_file, force_overwrite_to_cloud=True)
        print("Successfully uploaded to:", output_path)


if __name__ == "__main__":
    typer.run(main)
