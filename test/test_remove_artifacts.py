from typing import Dict, Tuple

from nbformat import NotebookNode
from traitlets.config import Config

from . import (  # noqa
    export,
    check_notebook_equivalence,
    notebook_basic,
    notebook_artifact_fake,
    notebook_artifact_file,
    notebook_artifact_named
)


def export_removing_artifacts(notebook: NotebookNode) -> Tuple[NotebookNode, Dict]:
    c = Config()
    c.NotebookExporter.preprocessors = [
        "nbconvert_inline_artifacts.ArtifactRemovePreprocessor"
    ]
    return export(c, notebook)


def test_no_artifact_idempotent(notebook_basic):    # noqa
    exported, _ = export_removing_artifacts(notebook_basic)
    check_notebook_equivalence(notebook_basic, exported)


def test_artifact_cell_removed_despite_no_artifact_string(
    notebook_basic,           # noqa
    notebook_artifact_fake    # noqa
):
    exported, _ = export_removing_artifacts(notebook_artifact_fake)
    check_notebook_equivalence(notebook_basic, exported)


def test_artifact_file_removed(notebook_basic, notebook_artifact_file):  # noqa
    exported, _ = export_removing_artifacts(notebook_artifact_file)
    check_notebook_equivalence(notebook_basic, exported)


def test_artifact_named_removed(notebook_basic, notebook_artifact_named):  # noqa
    exported, _ = export_removing_artifacts(notebook_artifact_named)
    check_notebook_equivalence(notebook_basic, exported)
