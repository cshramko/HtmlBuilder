#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
### DataClass for building, formatting, and rendering
### HTML pages across multiple functions and modules.
###
### To initialize:
###     from htmlbuilder import HTMLBuilder, SafeHTML
###     my_page = HTMLBuilder(title="My Page Title")
###

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

@dataclass
class SafeHTML:
    """A wrapper class for HTML content that is
    considered safe to render without escaping."""
    content: str

    def __str__(self) -> str:
        return self.content
# end class SafeHTML

class HTMLBuilder:
    """
    A class for building, formatting, and rendering HTML pages.
    
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
    """
    def __init__(self, title: str = "Untitled Page", css_files: Optional[List[str]] = None, js_files: Optional[List[str]] = None):
        self.title = title
        self.css_files = css_files if css_files is not None else []
        self.js_files = js_files if js_files is not None else []
        self.body_content: List[str] = []

    ###
    ### htmlbuilder Class Attributes
    ###

    title:       str = "Untitled Page"
    head:  List[str] = field(default_factory=list)
    body:  List[str] = field(default_factory=list)
    foot:  List[str] = field(default_factory=list)

    page_restore_points: Dict[str,Dict[str,int]] = field(default_factory=dict)
    body_restore_points: Dict[str,Dict[str,int]] = field(default_factory=dict)

    indent_level: int = 0
    indent_size:  int = 4

    ###
    ### Utility Methods
    ###

    def _validate_section_name(self, section_name: str) -> str:
        """
        Returns a section object if iit is on the allowed list:
            head, body, or foot
        Raises a ValueError if the section name is invalid.
        This prevents writing to non-appropriate attibutes.
        """
        allowed_sections = {'head', 'body', 'foot'}
        if section_name.strip() not in allowed_sections:
            raise ValueError(f"Invalid section name '{section_name}'. Must be one of: {', '.join(allowed_sections)}.")
        return str(section_name.strip())
    # end def _validate_section_name

    def _validate_attr_name(self, attr_name: str) -> str:
        """
        Validate HTML attribute names to prevent unsafe/injected attributes.
        Alllows only alphanumeric characters and hyphens.
        Rejects event handlers (on*).
        Raises a ValueError if the attribute name is invalid.  
        """
        if not re.match(r'^[a-zA-Z0-9-]+$', attr_name.strip()):
            raise ValueError(f"Invalid attribute name '{attr_name}'. Must be alphanumeric or hyphenated.")
        if attr_name.lower().startswith('on'):
            raise ValueError(f"Invalid attribute name '{attr_name}'. Event handler attributes are not allowed.")
        return str(attr_name.strip())
    # end def _validate_attr_name

    ###
    ### Escaping Non-Safe Content and Marking Safe HTML
    ###

    def escape_html(self, content: str) -> str:
        """
        Escape HTML content to prevent XSS attacks and ensure safe rendering.
        This method should be used for any content that is not explicitly marked as safe.
        """
        return html.escape(content)
    # end def escape_html

    def mark_safe(self, content: str) -> SafeHTML:
        """
        Mark content as safe HTML to prevent escaping.
        Use this method for content that is known to be safe and should not be escaped.
        """
        return SafeHTML(content)
    # end def mark_safe

    ###
    ### Raw HTML to Section Appenders
    ###

    def add_html_to_section(self, section_name: str, content: str) -> None:
        """
        Add raw HTML content to a specified section (head, body, or foot).
        This method does not escape the content, so it should be used with caution.
        """
        section_name = self._validate_section_name(section_name)
        if section_name == 'head':
            self.head.append(content)
        elif section_name == 'body':
            self.body.append(content)
        elif section_name == 'foot':
            self.foot.append(content)
    # end def add_html_to_section

    ###
    ### Text and Basic Content Appenders
    ###

    def add_text_to_section(self, section_name: str, text: str) -> None:
        """
        Add text content to a specified section (head, body, or foot).
        This method escapes the text to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_text = self.escape_html(text)
        self.add_html_to_section(section_name, escaped_text)
    # end def add_text_to_section

    def add_header_to_section(self, section_name: str, header_text: str, level: int = 1) -> None:
        """
        Add a header (h1, h2, etc.) to a specified section (head, body, or foot).
        The level parameter determines the header level (1-6).
        """
        if not (1 <= level <= 6):
            raise ValueError("Header level must be between 1 and 6.")
        section_name = self._validate_section_name(section_name)
        escaped_header_text = self.escape_html(header_text)
        header_html = f"<h{level}>{escaped_header_text}</h{level}>"
        self.add_html_to_section(section_name, header_html)
    # end def add_header_to_section

    def add_paragraph_to_section(self, section_name: str, paragraph_text: str) -> None:
        """
        Add a paragraph (<p>) to a specified section (head, body, or foot).
        This method escapes the paragraph text to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_paragraph_text = self.escape_html(paragraph_text)
        paragraph_html = f"<p>{escaped_paragraph_text}</p>"
        self.add_html_to_section(section_name, paragraph_html)
    # end def add_paragraph_to_section

    def add_list_to_section(self, section_name: str, items: Iterable[str], ordered: bool = False) -> None:
        """
        Add a list (<ul> or <ol>) to a specified section (head, body, or foot).
        The ordered parameter determines whether the list is ordered (<ol>) or unordered (<ul>).
        This method escapes the list items to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        list_tag = 'ol' if ordered else 'ul'
        escaped_items = [f"<li>{self.escape_html(item)}</li>" for item in items]
        list_html = f"<{list_tag}>\n" + "\n".join(escaped_items) + f"\n</{list_tag}>"
        self.add_html_to_section(section_name, list_html)   
    # end def add_list_to_section

    def add_table_to_section(self, section_name: str, headers: Iterable[str], rows: Iterable[Iterable[str]]) -> None:
        """
        Add a table (<table>) to a specified section (head, body, or foot).
        This method escapes the table headers and rows to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_headers = [f"<th>{self.escape_html(header)}</th>" for header in headers]
        header_html = "<tr>" + "".join(escaped_headers) + "</tr>"
        
        row_html_list = []
        for row in rows:
            escaped_row = [f"<td>{self.escape_html(cell)}</td>" for cell in row]
            row_html_list.append("<tr>" + "".join(escaped_row) + "</tr>")
        
        table_html = f"<table>\n{header_html}\n" + "\n".join(row_html_list) + "\n</table>"
        self.add_html_to_section(section_name, table_html)
    ### end def add_table_to_section

    def add_link_to_section(self, section_name: str, href: str, link_text: str) -> None:
        """
        Add a hyperlink (<a>) to a specified section (head, body, or foot).
        This method escapes the href and link text to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_href = self.escape_html(href)
        escaped_link_text = self.escape_html(link_text)
        
        link_html = f'<a href="{escaped_href}">{escaped_link_text}</a>'
        self.add_html_to_section(section_name, link_html)
    # end def add_link_to_section

    def add_newline_to_section(self, section_name: str = "body") -> None:
        """
        Add a newline (<br>) to a specified section (head, body, or foot).
        This method does not escape any content as it is a self-closing tag.
        """
        section_name = self._validate_section_name(section_name)
        br_html = "<br>"
        self.add_html_to_section(section_name, br_html)
    # end def add_newline_to_section

    def add_line_break_to_section(self, section_name: str = "body") -> None:
        """
        Add a line break (<br>) to a specified section (head, body, or foot).
        This method does not escape any content as it is a self-closing tag.
        """
        section_name = self._validate_section_name(section_name)
        br_html = "<br>"
        self.add_html_to_section(section_name, br_html)
    # end def add_line_break_to_section 

    def add_horizontal_rule_to_section(self, section_name: str = "body") -> None:
        """
        Add a horizontal rule (<hr>) to a specified section (head, body, or foot).
        This method does not escape any content as it is a self-closing tag.
        """
        section_name = self._validate_section_name(section_name)
        hr_html = "<hr>"
        self.add_html_to_section(section_name, hr_html)
    # end def add_horizontal_rule_to_section
    
    ###
    ### Block Elements with Optional Class Names
    ###

    def add_span_to_section(self, section_name: str, text: str, class_name: Optional[str] = None) -> None:
        """
        Add a span (<span>) to a specified section (head, body, or foot).
        This method escapes the text to ensure safe rendering.
        An optional class name can be provided for styling.
        """
        section_name = self._validate_section_name(section_name)
        escaped_text = self.escape_html(text)
        
        class_attr = f' class="{self.escape_html(class_name)}"' if class_name else ""
        
        span_html = f'<span{class_attr}>{escaped_text}</span>'
        self.add_html_to_section(section_name, span_html)
    # end def add_span_to_section

    def add_div_to_section(self, section_name: str, content: str, class_name: Optional[str] = None) -> None:
        """
        Add a div (<div>) to a specified section (head, body, or foot).
        This method escapes the content to ensure safe rendering.
        An optional class name can be provided for styling.
        """
        section_name = self._validate_section_name(section_name)
        escaped_content = self.escape_html(content)
        
        class_attr = f' class="{self.escape_html(class_name)}"' if class_name else ""
        
        div_html = f'<div{class_attr}>{escaped_content}</div>'
        self.add_html_to_section(section_name, div_html)
    # end def add_div_to_section

    def add_preformatted_text_to_section(self, section_name: str, text: str) -> None:
        """
        Add preformatted text (<pre>) to a specified section (head, body, or foot).
        This method escapes the text to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_text = self.escape_html(text)
        
        pre_html = f"<pre>{escaped_text}</pre>"
        self.add_html_to_section(section_name, pre_html)
    # end def add_preformatted_text_to_section

    def add_code_block_to_section(self, section_name: str, code: str) -> None:
        """
        Add a code block (<code>) to a specified section (head, body, or foot).
        This method escapes the code to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_code = self.escape_html(code)
        
        code_html = f"<code>{escaped_code}</code>"
        self.add_html_to_section(section_name, code_html)
    # end def add_code_block_to_section

    def add_blockquote_to_section(self, section_name: str, quote: str) -> None:
        """
        Add a blockquote (<blockquote>) to a specified section (head, body, or foot).
        This method escapes the quote to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_quote = self.escape_html(quote)
        
        blockquote_html = f"<blockquote>{escaped_quote}</blockquote>"
        self.add_html_to_section(section_name, blockquote_html)
    # end def add_blockquote_to_section

    # def add_css_file_to_section(self, section_name: str, css_file: str) -> None:
    #     """
    #     Add a CSS file to a specified section (head, body, or foot).
    #     """
    #     section_name = self._validate_section_name(section_name)
    #     self.css_files.append(css_file)
    # # end def add_css_file_to_section

    def add_css_class_to_section(self, section_name: str, class_name: str) -> None:
        """
        Add a CSS class to a specified section (head, body, or foot).
        This method escapes the class name to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_class_name = self.escape_html(class_name)
        
        class_html = f'<div class="{escaped_class_name}"></div>'
        self.add_html_to_section(section_name, class_html)
    # end def add_css_class_to_section

    def add_css_link_to_section(self, section_name: str, href: str) -> None:
        """
        Add a CSS link (<link>) to a specified section (head, body, or foot).
        This method escapes the href to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_href = self.escape_html(href)
        
        link_html = f'<link rel="stylesheet" type="text/css" href="{escaped_href}">'
        self.add_html_to_section(section_name, link_html)
    # end def add_css_link_to_section

    ###
    ### Images
    ###

    def add_image_to_section(self, section_name: str, src: str, alt: str = "", width: Optional[int] = None, height: Optional[int] = None) -> None:
        """
        Add an image (<img>) to a specified section (head, body, or foot).
        This method escapes the src and alt attributes to ensure safe rendering.
        Width and height can be specified as optional parameters.
        """
        section_name = self._validate_section_name(section_name)
        escaped_src = self.escape_html(src)
        escaped_alt = self.escape_html(alt)
        
        width_attr = f' width="{width}"' if width is not None else ""
        height_attr = f' height="{height}"' if height is not None else ""
        
        img_html = f'<img src="{escaped_src}" alt="{escaped_alt}"{width_attr}{height_attr}>'
        self.add_html_to_section(section_name, img_html)
    # end def add_image_to_section

    ###
    ### Scripts
    ###

    # def add_script_file_to_section(self, section_name: str, js_file: str) -> None:
    #     """
    #     Add a script file to a specified section (head, body, or foot).
    #     """
    #     section_name = self._validate_section_name(section_name)
    #     self.js_files.append(js_file)
    # # end def add_script_file_to_section

    def add_script_link_to_section(self, section_name: str, src: str) -> None:
        """
        Add a script (<script>) to a specified section (head, body, or foot).
        This method escapes the src attribute to ensure safe rendering.
        """
        section_name = self._validate_section_name(section_name)
        escaped_src = self.escape_html(src)
        
        script_html = f'<script src="{escaped_src}"></script>'
        self.add_html_to_section(section_name, script_html)
    # end def add_script_link_to_section

    def add_inline_script_to_section(self, section_name: str, script_content: str) -> None:
        """
        Add an inline script (<script>) to a specified section (head, body, or foot).
        This method does not escape the script content, so it should be used with caution.
        """
        section_name = self._validate_section_name(section_name)
        
        script_html = f'<script>{script_content}</script>'
        self.add_html_to_section(section_name, script_html)
    # end def add_inline_script_to_section

    ###
    ### Restore Points (Bookmarks for Rollback)
    ###

    def create_restore_point(self, section_name: str, restore_point_name: str) -> None:
        """
        Create a restore point (bookmark) for a specified section (head, body, or foot).
        This allows rolling back to a previous state of the section.
        """
        section_name = self._validate_section_name(section_name)
        restore_point_name = str(restore_point_name.strip())
        
        if section_name == 'head':
            self.page_restore_points[restore_point_name] = {'head': len(self.head)}
        elif section_name == 'body':
            self.page_restore_points[restore_point_name] = {'body': len(self.body)}
        elif section_name == 'foot':
            self.page_restore_points[restore_point_name] = {'foot': len(self.foot)}
    # end def create_restore_point

    def delete_restore_point(self, restore_point_name: str) -> None:
        """
        Delete a previously created restore point (bookmark).
        This removes the restore point and its associated state.
        """
        restore_point_name = str(restore_point_name.strip())
        
        if restore_point_name in self.page_restore_points:
            del self.page_restore_points[restore_point_name]
    # end def delete_restore_point

    def rollback_to_restore_point(self, section_name: str, restore_point_name: str) -> None:
        """
        Rollback a specified section (head, body, or foot) to a previously created restore point.
        This allows undoing changes made after the restore point was created.
        """
        section_name = self._validate_section_name(section_name)
        restore_point_name = str(restore_point_name.strip())
        
        if restore_point_name not in self.page_restore_points:
            raise ValueError(f"Restore point '{restore_point_name}' does not exist.")
        
        restore_point = self.page_restore_points[restore_point_name]
        
        if section_name == 'head':
            self.head = self.head[0:restore_point.get('head', len(self.head))]
        elif section_name == 'body':
            self.body = self.body[0:restore_point.get('body', len(self.body))]
        elif section_name == 'foot':
            self.foot = self.foot[0:restore_point.get('foot', len(self.foot))]
    # end def rollback_to_restore_point

    def create_page_restore_point(self, restore_point_name: str) -> None:
        """
        Create a restore point (bookmark) for the entire page (head, body, and foot).
        This allows rolling back to a previous state of the entire HTML page.
        """
        restore_point_name = str(restore_point_name.strip())
        
        self.page_restore_points[restore_point_name] = {
            'head': len(self.head),
            'body': len(self.body),
            'foot': len(self.foot)
        }
    # end def create_page_restore_point

    def rollback_to_page_restore_point(self, restore_point_name: str) -> None:
        """
        Rollback the entire page (head, body, and foot) to a previously created restore point.
        This allows undoing changes made after the restore point was created.
        """
        restore_point_name = str(restore_point_name.strip())
        
        if restore_point_name not in self.page_restore_points:
            raise ValueError(f"Restore point '{restore_point_name}' does not exist.")
        
        restore_point = self.page_restore_points[restore_point_name]
        
        self.head = self.head[:restore_point.get('head', len(self.head))]
        self.body = self.body[:restore_point.get('body', len(self.body))]
        self.foot = self.foot[:restore_point.get('foot', len(self.foot))]
    # end def rollback_to_page_restore_point

    def clear_section(self, section_name: str) -> None:
        """
        Clear all content from a specified section (head, body, or foot).
        This removes all elements from the section.
        """
        section_name = self._validate_section_name(section_name)
        
        if section_name == 'head':
            self.head.clear()
        elif section_name == 'body':
            self.body.clear()
        elif section_name == 'foot':
            self.foot.clear()
    # end def clear_section

    def clear_all_sections(self) -> None:
        """
        Clear all content from all sections (head, body, and foot).
        This removes all elements from the entire HTML page.
        """
        self.head.clear()
        self.body.clear()
        self.foot.clear()
    # end def clear_all_sections

    ###
    ### Rendering Methods
    ###

    def render(self) -> str:
        """
        Render the HTML page with automatic indentation
        based on tag nesting depth. Examines each line to
        determine whether it is an opening tag, closing tag,
        or self-closing tag, and adjusts the indentation
        level accordingly. Returns the final HTML as a string.
        """
        def is_opening_tag(line: str) -> bool:
            # <div>, <p>, <h1>, etc. but not </div> or <!DOCTYPE html>
            return re.match(r'^\s*<[^/!][^>]*?>', line) is not None

        def is_closing_tag(line: str) -> bool:
            # </div>, </p>, </h1>, etc.
            return re.match(r'^\s*</[^>]+?>', line) is not None

        def is_self_closing_tag(line: str) -> bool:
            # <img />, <br />, <hr />, etc.
            return re.match(r'^\s*<[^>]+?/>', line) is not None

        head_content   = "\n".join(self.head)
        head_content   = "<!DOCTYPE html>\n<html>\n<head>\n" + head_content + "\n</head>\n"
        
        body_content   = "\n".join(self.body)
        body_content   = "<body>\n" + body_content + "\n</body>\n"
        
        foot_content   = "\n".join(self.foot)
        foot_content   = "<footer>\n" + foot_content + "\n</footer>\n"

        page_content   = head_content.splitlines() + body_content.splitlines() + foot_content.splitlines()
        
        indented_lines = []

        for line in page_content:

            stripped_line = line.strip()

            # closing tags reduce indentation level before adding the line
            if is_closing_tag(stripped_line):
                self.indent_level = max(self.indent_level - 1, 0)

            # Add the line with the current indentation level
            indented_lines.append(" " * (self.indent_level * self.indent_size) + stripped_line)

            # opening tags increase indentation level after adding the line
            # self-closing tags do not affect indentation level
            if is_opening_tag(stripped_line) and not is_self_closing_tag(stripped_line):
                self.indent_level += 1

        # Close the HTML tag at the end
        indented_lines.append("</html>")  

        return "\n".join(indented_lines)
    # end def render

    def render_to_file(self, file_path: str) -> None:
        """
        Render the HTML page and write it to a specified file.
        This method creates the file if it does not exist and overwrites it if it does.
        """
        html_content = self.render()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    # end def render_to_file

    def render_to_file_and_open(self, file_path: str) -> None:
        """
        Render the HTML page, write it to a specified file, and open it in the default web browser.
        This method creates the file if it does not exist and overwrites it if it does.
        """
        self.render_to_file(file_path)
        import webbrowser
        webbrowser.open(f'file://{Path(file_path).resolve()}')  
    # end def render_to_file_and_open

    def render_to_path(self, path: str) -> None:
        """
        Render the HTML page and write it to a specified path.
        This method creates the file if it does not exist and overwrites it if it does.
        """
        self.render_to_file(path)
    # end def render_to_path

    def render_to_path_and_open(self, path: str) -> None:
        """
        Render the HTML page, write it to a specified path, and open it in the default web browser.
        This method creates the file if it does not exist and overwrites it if it does.
        """
        self.render_to_file(path)
        import webbrowser
        webbrowser.open(f'file://{Path(path).resolve()}')   
    # end def render_to_path_and_open

    def render_to_email_message(self, subject: str, from_addr: str, to_addrs: List[str]) -> Any:
        """
        Render the HTML page and create an email message object with the rendered HTML as the body.
        This method requires the 'email' and 'smtplib' modules.
        """
        import email.message

        html_content = self.render()
        
        msg = email.message.EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        msg.set_content("This is an HTML email. Please view it in an HTML-compatible email client.")
        msg.add_alternative(html_content, subtype='html')
        
        return msg
    # end def render_to_email_message

    def render_to_pdf(self, output_path: str) -> None:
        """
        Render the HTML page and convert it to a PDF file at the specified output path.
        This method requires the 'pdfkit' module and a working installation of wkhtmltopdf.
        """
        import pdfkit
        import tempfile
        import os

        html_content = self.render()
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html_file:
            temp_html_file.write(html_content.encode('utf-8'))
            temp_html_path = temp_html_file.name
        
        # Convert the temporary HTML file to PDF
        pdfkit.from_file(temp_html_path, output_path)
        
        # Clean up the temporary HTML file
        os.remove(temp_html_path)
    # end def render_to_pdf

    # def render_to_docx(self, output_path: str) -> None:
    #     """
    #     Render the HTML page and convert it to a 
    #     DOCX file at the specified output path.
    #     This method requires the 'python-docx' module.
    #     """
    #     import docx

    #     html_content = self.render()
        
    #     # Create a new DOCX document
    #     doc = docx.Document()
        
    #     # Add the HTML content as a single paragraph (for simplicity)
    #     doc.add_paragraph(html_content)
        
    #     # Save the DOCX document
    #     doc.save(output_path)   
    # # end def render_to_docx

    def render_to_bytes(self) -> bytes:
        """
        Render the HTML page and return it as a bytes object.
        This can be useful for sending the HTML content over 
        a network or saving it in a binary format.
        """
        html_content = self.render()
        return html_content.encode('utf-8')
    # end def render_to_bytes

    def render_to_http_response(self) -> Any:
        """
        Render the HTML page and return it as an HTTP response object.
        This method is designed for use with web frameworks 
        that support HTTP responses.
        """
        from flask import Response  # Example for Flask; adjust for other frameworks as needed
        html_content = self.render()
        return Response(html_content, mimetype='text/html') 
    # end def render_to_http_response

    def render_to_markdown(self) -> str:
        """
        Render the HTML page and convert it to Markdown format.
        This method uses a simple conversion approach and 
        may not handle all HTML elements perfectly.
        """
        import re

        markdown_content = self.render()
        
        # Headers <h1> to <h6> to Markdown headers  
        for i in range(6, 0, -1):
            markdown_content = re.sub(
                rf'<h{i}>(.*?)</h{i}>',
                rf'{"#" * i} \1',
                markdown_content,
                flags=re.DOTALL)

        # Paragraphs <p> to Markdown paragraphs
        markdown_content = re.sub(
            r'<p>(.*?)</p>', 
            r'\1\n', 
            markdown_content, 
            flags=re.DOTALL)

        # Iamges <img> to Markdown images
        markdown_content = re.sub(
            r'<img src="(.*?)" alt="(.*?)".*?>', 
            r'![\2](\1)', 
            markdown_content, 
            flags=re.DOTALL)

        # Links <a> to Markdown links
        markdown_content = re.sub(
            r'<a href="(.*?)">(.*?)</a>', 
            r'[\2](\1)', 
            markdown_content, 
            flags=re.DOTALL)

        # Blockquotes <blockquote> to Markdown blockquotes
        markdown_content = re.sub(
            r'<blockquote>(.*?)</blockquote>', 
            r'> \1', 
            markdown_content, 
            flags=re.DOTALL)

        # Lists <ul> and <ol> to Markdown lists
        markdown_content = re.sub(
            r'<ul>(.*?)</ul>', 
            lambda m: '\n'.join(f'- {item.strip()}' for item in re.findall(r'<li>(.*?)</li>', m.group(1), flags=re.DOTALL)), 
            markdown_content, 
            flags=re.DOTALL)

        # Tables <table> to Markdown tables (basic conversion)
        markdown_content = re.sub(
            r'<table>(.*?)</table>', 
            lambda m: '\n'.join(
                '| ' + ' | '.join(cell.strip() for cell in re.findall(r'<t[dh]>(.*?)</t[dh]>', row, flags=re.DOTALL)) + ' |'
                for row in re.findall(r'<tr>(.*?)</tr>', m.group(1), flags=re.DOTALL)
            ), 
            markdown_content, 
            flags=re.DOTALL)

        # Remove any remaining HTML tags
        markdown_content = re.sub(
            r'<[^>]+>', 
            '', 
            markdown_content)    

        # Strip leading/trailing whitespace  
        markdown_content = re.sub(r'^\s+|\s+$', '', markdown_content)   

        # Convert 3 or more consecutive newlines
        # with or without whitespace 2 newlines 
        markdown_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_content)
        
        return markdown_content.strip()
    # end def render_to_markdown

# end class HTMLBuilder

#### End of htmlbuilder.py
