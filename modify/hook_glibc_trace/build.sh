SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit

docker build -t build-env .
docker run --rm -v $(pwd):/output build-env cp hook_glibc_trace.so /output
