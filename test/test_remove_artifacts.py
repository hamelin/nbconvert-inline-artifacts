from typing import Dict, Tuple

from nbformat import NotebookNode
from traitlets.config import Config

from . import (  # noqa
    export,
    check_notebook_equivalence,
    notebook_basic,
    notebook_artifact_fake,
    notebook_artifact_file,
    notebook_artifacts
)


def export_removing_artifacts(notebook: NotebookNode) -> Tuple[NotebookNode, Dict]:
    c = Config()
    c.NotebookExporter.preprocessors = [
        "nbcomvert_html_complex.ArtifactRemovePreprocessor"
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


def test_artifacts_all_removed(notebook_basic, notebook_artifacts):  # noqa
    exported, _ = export_removing_artifacts(notebook_artifacts)
    check_notebook_equivalence(notebook_basic, exported)
