# -*- coding: latin-1 -*-
"""
We do not accept bogus inline template such as ones that contain
encoded strings:

  >>> import grok
  >>> grok.PageTemplate('''
  ... <html>
  ... <body><h1 tal:content="string:Mammoth Cave Painting"/>
  ... <p>���</p>
  ... </body>
  ... </html>''')
  Traceback (most recent call last):
    ...
  GrokError: Invalid page template. Page templates must be unicode or ASCII.
"""
