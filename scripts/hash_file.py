from base64 import urlsafe_b64encode
from hashlib import md5
from pathlib import Path
import sys

from xxhash import xxh64


def main(input_file: Path):
    content = input_file.read_bytes()
    md5sum = md5(content)
    xxh64sum = xxh64(content)
    print("md5sum: ", md5sum.hexdigest())
    print("xxh64sum: ", xxh64sum.hexdigest())
    print("b64(xxh64sum): ", urlsafe_b64encode(xxh64sum.digest()).decode().strip("="))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
