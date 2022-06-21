from base64 import b64encode
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Tuple

from nbconvert.preprocessors import Preprocessor, TagRemovePreprocessor
from nbformat import NotebookNode
from traitlets import HasTraits
from traitlets.traitlets import Set, Unicode, Dict, Bytes


class ArtifactRemovePreprocessor(TagRemovePreprocessor):
    """
    Preprocessor that removes notebook cells that carry the tag ``artifact``. This is
    useful for producing multiple versions of a notebook rendering: one with, say,
    a printable PDF copy of the notebook, and a HTML or notebook container. The former
    would be produced with ``nbconvert`` using this preprocessor, and the latter
    would instead use the :class:`.ArtifactEmbedPreprocessor`.
    """
    remove_cell_tags = Set(
        Unicode(),
        default_value=["artifact"],
        help=(
            "Tags indicating cells to remove; already configured, change this only if "
            "you know what you are doing."
        )
    )


@dataclass
class InvalidArtifactDescriptor(Exception):
    descriptor: str


@dataclass
class InaccessibleFileArtifact(Exception):
    path: Path


@dataclass
class UnknownNamedArtifact(Exception):
    identifier: str


class Artifact(HasTraits):
    info_text = "Binary artifact characterized by its MIME type and composing bytes."
    mime_type = Unicode(
        default_value="application/octet-stream",
        help="MIME type of the artifact"
    )
    content = Bytes(help="Contents of the artifact")


class ArtifactEmbedPreprocessor(Preprocessor):
    """
    Preprocessor that substitutes artifact descriptions with a
    ``data:mime/type,base64 ...`` URL. An artifact description itself is a URL-like
    string. It may take any of the following two forms. The first:

    ``artifact:mime/type:path/on/the/file/system``

    Such paths are resolved relative to the current directory. An absolute path can
    be provided by following the colon with 3 slashes: ``artifact:///absolute/path``.
    This path should correspond to a file or file-like device that can be read as a
    string of bytes. Note also that this path must be URL-encoded: no space or quote
    character allowed. This includes single quotes ('), double quotes (") and back
    quotes (`). The second form:

    ``artifact::identifier``

    In this case, the identifier must be composed of letters, digits, underscores and
    hyphens (-). It is resolved using the preprocessor's :attr:`artifacts` map, which
    associates such identifiers to byte strings.
    """
    artifacts = Dict(Artifact, help="Resolvable artifacts.")

    def resolve_artifact(self, m: re.Match) -> str:
        if m["path"] and m["identifier"]:
            raise InvalidArtifactDescriptor(m.group(0))
        if not (m["path"] or m["identifier"]):
            raise InvalidArtifactDescriptor(m.group(0))

        content: bytes
        if m["path"]:
            mime_type = m["mime_type"]
            path = Path(m["path"])
            if not path.is_file():
                raise InaccessibleFileArtifact(path)
            content = Path(m["path"]).read_bytes()
        elif m["identifier"]:
            if m["identifier"] not in self.artifacts:
                raise UnknownNamedArtifact(m["identifier"])
            artifact = self.artifacts[m["identifier"]]
            mime_type, content = artifact.mime_type, artifact.content
        else:
            raise RuntimeError("Problem with decoding of artifact descriptors.")
        return f'data:{mime_type};base64,{b64encode(content).decode("ascii")}'

    def preprocess_cell(
        self,
        cell: NotebookNode,
        resources: Dict,
        index: int
    ) -> Tuple[NotebookNode, Dict]:
        tags = set(cell.get("metadata", {}).get("tags", []))
        if "artifact" in tags:
            source = cell.source
            while True:
                resolved = re.sub(
                    (
                        r"artifact:((?P<mime_type>[-_a-zA-Z0-9/]+)"
                        r""":(?P<path>[^ :'"`)>]+)|"""
                        r"""(:(?P<identifier>[-_a-zA-Z0-9]+)))"""
                    ),
                    self.resolve_artifact,
                    source
                )
                if resolved == source:
                    break
                source = resolved
            cell.source = resolved
        return cell, resources
