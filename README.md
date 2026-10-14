# HtmlBuilder

```
    DataClass for building, formatting, and rendering
    HTML pages across multiple functions and modules.

    Required Internal Imports:
        import html
        import re
        from dataclasses import dataclass, field
        from pathlib import Path
        from typing import Any, Dict, Iterable, List, Optional

    Methods Requiring Additional Internal Imports:
    
        render_to_file_and_open()
            import webbrowser

        render_to_path_and_open()
            import webbrowser
        
        render_to_email_message()
            import email.message

        render_to_pdf()
            import pdfkit
            import tempfile
            import os
        
        render_to_docx()
            import docx

        render_to_http_response()
            from flask import Response  # Example for Flask; adjust for other frameworks as needed

        render_to_markdown()
            import re

        Usage Example:

            from htmlbuilder import HTMLBuilder, SafeHTML

            # Create an instance of HTMLBuilder
            my_page = HTMLBuilder(title="My Page Title")

            # Add CSS and JS files
            my_page.add_css("styles.css")
            my_page.add_js("script.js")

            # Add body content
            my_page.add_body_content("<h1>Welcome to My Page</h1>")
            my_page.add_body_content("<p>This is a sample paragraph.</p>")

            # Render the HTML page as a string
            html_string = my_page.render()

            # Optionally, render to a file and open in a web browser
            my_page.render_to_file_and_open("my_page.html")
```

## License
See [LICENSE](LICENSE).
