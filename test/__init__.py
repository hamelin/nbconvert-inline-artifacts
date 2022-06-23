from copy import deepcopy
from io import StringIO
from typing import Dict, Tuple

from nbconvert import NotebookExporter
from nbformat import NotebookNode, read, NO_CONVERT, from_dict as notebook_from_dict
import pytest
from traitlets.config import Config


def export(config: Config, notebook: NotebookNode) -> Tuple[NotebookNode, Dict]:
    exported_content, resources = NotebookExporter(config).from_notebook_node(notebook)
    return read(StringIO(exported_content), NO_CONVERT), resources


def flatten_text(cplx):
    if isinstance(cplx, list) and len(cplx) > 0 and isinstance(cplx[0], str):
        return "".join(cplx)
    elif isinstance(cplx, dict):
        return {key: flatten_text(value) for key, value in cplx.items()}
    elif isinstance(cplx, list):
        return [flatten_text(v) for v in cplx]
    else:
        return cplx


def check_notebook_equivalence(ideal, trial, idx=[]):
    assert ideal.metadata == trial.metadata
    assert len(ideal.cells) == len(trial.cells)
    if not idx:
        idx = range(len(ideal.cells))
    for i in idx:
        assert flatten_text(ideal.cells[i]) == flatten_text(trial.cells[i])


@pytest.fixture
def notebook_basic() -> NotebookNode:
    return notebook_from_dict(
        {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": 1,
                    "id": "cb7af8cf-c52b-42a2-96e4-b17c258864ab",
                    "metadata": {},
                    "outputs": [
                        {
                            "data": {
                                "text/plain": [
                                    "15"
                                ]
                            },
                            "execution_count": 1,
                            "metadata": {},
                            "output_type": "execute_result"
                        }
                    ],
                    "source": [
                        "# Some code\n",
                        "a = 5\n",
                        "b = 10\n",
                        "a + b"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "id": "c1ea81d3-89d4-4a83-ab2b-cc5edd2ca6bf",
                    "metadata": {},
                    "source": [
                        "Some text.\n",
                        "\n",
                        "More text here. No artifact."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": 2,
                    "id": "f3ce15a5-f520-4414-9b33-7db87cefc6ff",
                    "metadata": {},
                    "outputs": [
                        {
                            "data": {
                                "text/plain": [
                                    "50"
                                ]
                            },
                            "execution_count": 2,
                            "metadata": {},
                            "output_type": "execute_result"
                        }
                    ],
                    "source": [
                        "a * b"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "nbconvert-html-complex (Python)",
                    "language": "python",
                    "name": "conda-env-nbconvert-html-complex-py"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.10.4"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
    )


@pytest.fixture
def notebook_artifact_fake(notebook_basic):
    nb = deepcopy(notebook_basic)
    nb.cells.append(
        notebook_from_dict({
            "cell_type": "markdown",
            "id": "c1ea81d3-89d4-4a83-ab2b-cc5ddd2ca6bf",
            "metadata": {
                "tags": [
                    "artifact"
                ]
            },
            "source": (
                "Some more text. No artifact here despite tags.\n"
            )
        })
    )
    return nb


@pytest.fixture
def notebook_artifact_file(notebook_artifact_fake):
    nb = deepcopy(notebook_artifact_fake)
    nb.cells.append(
        notebook_from_dict({
            "cell_type": "markdown",
            "id": "c1ea81d3-89d4-4a83-ab2b-cc5ddd2da6bf",
            "metadata": {
                "tags": [
                    "artifact"
                ]
            },
            "source": (
                "Finally a real "
                """<a href="artifact:image/png:test/some-image.png">artifact</a>!""",
            )
        })
    )
    return nb


@pytest.fixture
def notebook_artifact_named(notebook_artifact_fake):
    nb = deepcopy(notebook_artifact_fake)
    nb.cells.append(
        notebook_from_dict({
            "cell_type": "markdown",
            "id": "c1ea81dd-89d4-4a83-ab2b-cc5ddd2da6bf",
            "metadata": {
                "tags": [
                    "artifact"
                ]
            },
            "source": (
                """And then one <embed type="application/pdf" src="artifact::my-pdf">"""
                "from</embed> a map."
            )
        })
    )
    return nb
