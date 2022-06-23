# External artifacts inlining in web-able documents  using `jupyter nbconvert`

Web-able documents, typically based on HTML 5, such as ye olde webpage or as Jupyter notebooks, facilitate document associations through hyperlinking. However, there are situations where we would rather contain subdocuments *inline* rather than as separate files. For instance, if one is to send a report that includes figures, one must care to include all those as separate image files from some HTML document where the report is written, and then hope that the recipient unpacks all of that into a common directory. Another example is for documents declined in distinct formats -- audience member reading the document off of a screen may prefer having a HTML document that typesets according to their preferences and constraints, whereas folks that prefer reading off of paper will prefer having a well-typeset PDF file to send to the printer (given how printing on most web browsers is an tacked-on, disused feature). In both cases, one would rather incorporate all figures or alternative declinations of the document into a single file.

A common [URL specification](https://datatracker.ietf.org/doc/html/rfc2397) enables such incorporation: the data that make up images or alternative documents is embedded directly as into the URL. Modern web browsers support such *data URLs* fully, either displaying such embedded images as if they were externally linked, or enabling the user to "download" inline documents as if they were hosted remotely.
However, document authoring tools do not make the addition of such inline artifacts easy. The tools of this project aim at filling this gap when the document being authored is a Jupyter notebook, which can be processed into a form distributable on the web: HTML, Markdown, even merely a modified notebook; using `jupyter nbconvert`

## Specifying artifacts to inline

## Building the final document from the command line

## Scripting the final document build in Python
