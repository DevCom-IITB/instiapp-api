"""Extra custom tests."""
from helpers.misc import table_to_markdown

# Test table_to_markdown
table_to_markdown("""<table>
<tr><td>H1</td><td>H2</td></tr>
<tr><td>D1</td><td>D2</td></tr>
</table>""")
table_to_markdown("""<table>
<tr><td>H1</td></tr>
<tr><td>D1</td><td>D2</td></tr>
</table>""")
table_to_markdown("""<table>
<tr><td>H1</td></tr>
<tr><td>D1</td></tr>
</table>""")
table_to_markdown("""<table>
<tr></tr>
<tr></tr>
</table>""")
table_to_markdown("")
