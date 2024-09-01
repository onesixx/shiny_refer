import markdown

with open("README.md", 'r', encoding='utf-8') as md_file:
    md_content = md_file.read()

html_content = markdown.markdown(md_content)

with open("README.html", 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

print("Convert Markdown to HTML")