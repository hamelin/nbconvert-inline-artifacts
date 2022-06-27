from base64 import b64encode
from pathlib import Path
from typing import Tuple, Dict

from nbformat import NotebookNode
import pytest
from traitlets.config import Config

from nbconvert_inline_artifacts import UnknownNamedArtifact, InaccessibleFileArtifact
from . import (  # noqa
    export,
    flatten_text,
    check_notebook_equivalence,
    notebook_basic,
    notebook_artifact_file,
    notebook_artifact_named
)


def export_substituting_artifacts(
    notebook: NotebookNode,
    config: Config = Config()
) -> Tuple[NotebookNode, Dict]:
    config.NotebookExporter.preprocessors = [
        "nbconvert_inline_artifacts.ArtifactEmbedPreprocessor"
    ]
    return export(config, notebook)


def test_no_artifact_to_sub(notebook_basic):  # noqa
    exported, _ = export_substituting_artifacts(notebook_basic)
    check_notebook_equivalence(notebook_basic, exported)


def test_sub_artifact_file(notebook_artifact_file):  # noqa
    exported, _ = export_substituting_artifacts(notebook_artifact_file)
    check_notebook_equivalence(
        notebook_artifact_file,
        exported,
        range(len(notebook_artifact_file) - 1)
    )
    assert (
        (
            '<a href="data:image/png;base64,' + b64encode(
                Path("test/some-image.png").read_bytes()
            ).decode("ascii") + '">artifact</a>'
        )
        in flatten_text(exported.cells[-1]["source"])
    )


def test_sub_artifact_named(notebook_artifact_named):  # noqa
    c = Config()
    c.ArtifactEmbedPreprocessor.artifacts = {
        "my-pdf": {
            "mime_type": "application/pdf",
            "content": Path("test/example.pdf").read_bytes()
        }
    }
    exported, _ = export_substituting_artifacts(notebook_artifact_named, c)
    check_notebook_equivalence(
        notebook_artifact_named,
        exported,
        range(len(notebook_artifact_named) - 1)
    )
    assert (
        (
            (
                '<embed type="application/pdf" '
                'src="data:application/pdf;base64,'
            ) + b64encode(
                Path("test/example.pdf").read_bytes()
            ).decode("ascii") + '">from</embed>'
        )
        in flatten_text(exported.cells[-1]["source"])
    )


def test_sub_artifact_named_absent(notebook_artifact_named):  # noqa
    with pytest.raises(UnknownNamedArtifact):
        export_substituting_artifacts(notebook_artifact_named)


def test_sub_artifact_file_absent(notebook_artifact_file):  # noqa
    notebook_artifact_file.cells[-1]["source"] = (
        flatten_text(notebook_artifact_file.cells[-1]["source"]).replace(
            "test/some-image.png",
            "test/no-estoy-aqui-senor.png"
        )
    )
    with pytest.raises(InaccessibleFileArtifact):
        export_substituting_artifacts(notebook_artifact_file)
