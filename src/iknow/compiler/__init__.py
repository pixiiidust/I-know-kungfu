"""Draft Wiki Compiler module.

Seam: compile selected sources plus a Wiki Contract into a Reviewable Private
Draft Wiki (raw Markdown mirror, source manifest, index.json, llms.txt,
warnings, review notes).

v1 adapter: local filesystem read/write. No hosted artifact store.
"""

from iknow.compiler.config import CompilerConfig, parse_config
from iknow.compiler.manifest import SourceManifest, build_manifest
from iknow.compiler.compile import compile_draft, CompileResult
from iknow.compiler.artifacts import write_artifacts

__all__ = [
    "CompilerConfig",
    "parse_config",
    "SourceManifest",
    "build_manifest",
    "compile_draft",
    "CompileResult",
    "write_artifacts",
]
