# External artifacts inlining in web-able documents  using `jupyter nbconvert`

Web-able documents, typically based on HTML 5, such as ye olde webpage or as Jupyter notebooks, facilitate document associations through hyperlinking. However, there are situations where we would rather contain subdocuments *inline* rather than as separate files. For instance, if one is to send a report that includes figures, one must care to include all those as separate image files from some HTML document where the report is written, and then hope that the recipient unpacks all of that into a common directory. Another example is for documents declined in distinct formats -- audience member reading the document off of a screen may prefer having a HTML document that typesets according to their preferences and constraints, whereas folks that prefer reading off of paper will prefer having a well-typeset PDF file to send to the printer (given how printing on most web browsers is an tacked-on, disused feature). In both cases, one would rather incorporate all figures or alternative declinations of the document into a single file.

A common [URL specification](https://datatracker.ietf.org/doc/html/rfc2397) enables such incorporation: the data that make up images or alternative documents is embedded directly as into the URL. Modern web browsers support such *data URLs* fully, either displaying such embedded images as if they were externally linked, or enabling the user to "download" inline documents as if they were hosted remotely.
However, document authoring tools do not make the addition of such inline artifacts easy.
This project aim at filling this gap when the document being authored is a Jupyter notebook, which can be processed into a form distributable on the web: HTML, Markdown, even merely a modified notebook.
The key consists in a `jupyter nbconvert` [preprocessor](https://nbconvert.readthedocs.io/en/latest/api/preprocessors.html).

## Usage

First step is to write up a [Jupyter notebook](https://jupyter.org/try-jupyter/lab/). Even folks who don't require interactive computation can make good, productive use of Jupyter as an authoring environment based on [Markdown](https://www.markdownguide.org/basic-syntax/) notation.

### Inlining external files

*Inlining* external *artifacts* refers to the incorporation of assets usually stored in external files, such as images and alternative texts, directly in the core document, in the form of [data URLs](https://datatracker.ietf.org/doc/html/rfc2397).
As suggested, this can be figures, or other documents one would want to bundle with their main text so they can be "downloaded offline," so to speak.
Such artifacts must be described among the Markdown cells of the notebook in any place one would otherwise write up a URL. The artifact description is as follows:

    artifact:mime/type:path/to/file/to/inline

Event on Windows, components of the path must be separated by forward slashes (`/`).
Examples:

| Notation | Purpose           | Artifact description in context                                                                    |
|:--------:|:------------------|:---------------------------------------------------------------------------------------------------|
| Markdown | Figure            | `![Alt text](artifact:image/png:images/figure.png)`                                                |
|          | Embedded document | `[Text of the link](artifact:application/pdf:embed-this.pdf)`                                      |
| HTML     | Figure            | `<img src="artifact:image/png:images/figure.png" alt="Alt text">`                                  |
|          | Embedded document | `<a href="artifact:application/pdf:embed-this.pdf" download="embed-this.pdf">Text of the link</a>` |

### Building the incorporated document from the command line

One can produce the document with embedded artifacts with a command such as this:

```sh
jupyter nbconvert --preprocessors nbconvert_inline_artifacts.ArtifactInlinePreprocessor #... <rest of the command>
```

For instance, to export a HTML file with inline artifacts:

```sh
jupyter nbconvert --preprocessors nbconvert_inline_artifacts.ArtifactInlinePreprocessor --to html document-as-notebook.ipynb
```

### Scripting the incorporated document build in Python

The nbconvert tool is also productively used from a [Python scripting](https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html) perspective.
This usage pattern enables the inlining of artifacts that exist in a process' memory, as opposed to external files. Such artifacts are *named* instead using a unique identifier, which is mapped in turn to an artifact expressed as a Python bytes string.
For instance, consider a source notebook where one Markdown cell tagged `pdf-version` contains the following text:

    [Get the PDF version](artifact::pdf)

The following script would generate first a PDF version of this notebook (requires a LaTeX install and Pandoc) without that cell, then a HTML version where that PDF version is inlined:

```python
from nbconvert import PDFExporter, HTMLExporter
from traitlets.config import Config

c_pdf = Config()
c_pdf.Exporter.preprocessors = ["nbconvert.preprocessors.TagRemovePreprocessor"]
c_pdf.TagRemovePreprocessor.remove_cell_tags = ["pdf-version"]
pdf_exporter = PDFExporter(config=c_pdf)
pdf = pdf_exporter.from_filename("document.ipynb")

c_html = Config()
c_html.Exporter.preprocessors = ["nbconvert_inline_artifacts.ArtifactInlinePreprocessor"]
c_html.ArtifactInlinePreprocessor.artifacts = {"pdf": pdf}
html_exporter = HTMLExporter(config=c_html)
with open("document.html", "wb") as file:
    file.write(pdf_exporter.from_filename("document.ipynb"))
```

Look [here](examples/fileless_document_conversion/conversion.ipynb) for a larger example.

## Development

The development environment is put together easily using [Conda](https://docs.conda.io/en/latest/):

```sh
conda env create
```

Checks on PEP8 conformance, typing coherence and unit tests:

```sh
conda run -n nbconvert-inline-artifacts --no-capture-output python script/checks.py
```
