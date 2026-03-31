from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from ..exceptions import ArtifactError


# ---------------------------------------------------------------------------
# ArtifactStore protocol
# ---------------------------------------------------------------------------

class ArtifactStore(ABC):
    """Abstract base for artifact backends (local filesystem, S3, etc.)."""

    @abstractmethod
    def upload(self, local_path: Path, artifact_name: str) -> str:
        """Upload a local file. Returns a URI or path string."""

    @abstractmethod
    def download(self, artifact_name: str, dest: Path) -> Path:
        """Download artifact to dest. Returns the resolved destination path."""

    @abstractmethod
    def exists(self, artifact_name: str) -> bool:
        """Return True if the artifact exists in the store."""


# ---------------------------------------------------------------------------
# Local filesystem store
# ---------------------------------------------------------------------------

class LocalArtifactStore(ArtifactStore):
    """
    Stores artifacts in a local directory tree.
    Suitable for single-machine builds or CI systems with shared volumes.
    """

    def __init__(self, base_dir: Path | str) -> None:
        self._base = Path(base_dir).resolve()
        self._base.mkdir(parents=True, exist_ok=True)

    def upload(self, local_path: Path, artifact_name: str) -> str:
        dest = self._base / artifact_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dest)
        return str(dest)

    def download(self, artifact_name: str, dest: Path) -> Path:
        src = self._base / artifact_name
        if not src.exists():
            raise ArtifactError(f"Artifact '{artifact_name}' not found in {self._base}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return dest.resolve()

    def exists(self, artifact_name: str) -> bool:
        return (self._base / artifact_name).exists()

    def publish(self, artifact_name: str, tag: str = "latest") -> str:
        """
        Create a tagged alias of an artifact (hard link, falling back to copy).
        Returns the path of the published alias.
        """
        src = self._base / artifact_name
        if not src.exists():
            raise ArtifactError(f"Artifact '{artifact_name}' not found")
        stem = Path(artifact_name)
        tagged_name = str(stem.parent / f"{stem.stem}.{tag}{stem.suffix}")
        link = self._base / tagged_name
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.exists():
            link.unlink()
        try:
            link.hardlink_to(src)
        except (OSError, NotImplementedError):
            shutil.copy2(src, link)
        return str(link)


# ---------------------------------------------------------------------------
# S3-compatible store (requires boto3)
# ---------------------------------------------------------------------------

class S3ArtifactStore(ArtifactStore):
    """
    S3-compatible artifact store.

    Requires boto3: ``pip install prebuildci[s3]``

    :param bucket: S3 bucket name.
    :param prefix: Optional key prefix (e.g. "builds/my-project/").
    :param region: AWS region.
    :param endpoint_url: Override endpoint for MinIO / LocalStack.
    """

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        region: str = "us-east-1",
        endpoint_url: str | None = None,
    ) -> None:
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3ArtifactStore. "
                "Install with: pip install prebuildci[s3]"
            )
        self._bucket = bucket
        self._prefix = prefix
        self._s3 = boto3.client("s3", region_name=region, endpoint_url=endpoint_url)

    def _key(self, name: str) -> str:
        return f"{self._prefix}{name}" if self._prefix else name

    def upload(self, local_path: Path, artifact_name: str) -> str:
        key = self._key(artifact_name)
        self._s3.upload_file(str(local_path), self._bucket, key)
        return f"s3://{self._bucket}/{key}"

    def download(self, artifact_name: str, dest: Path) -> Path:
        key = self._key(artifact_name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._s3.download_file(self._bucket, key, str(dest))
        return dest.resolve()

    def exists(self, artifact_name: str) -> bool:
        import botocore.exceptions
        try:
            self._s3.head_object(Bucket=self._bucket, Key=self._key(artifact_name))
            return True
        except botocore.exceptions.ClientError:
            return False


