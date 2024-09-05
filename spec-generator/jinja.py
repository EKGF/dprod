import jinja2


def generate_spec_page(jinja_context):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./respec/"))
    template = env.get_template("template.html")
    spec = template.render(jinja_context)
    with open('dist/index.html', mode='x', encoding='utf-8') as f:
        print(f"Generating spec page: ./{f.name}")
        f.write(spec)
