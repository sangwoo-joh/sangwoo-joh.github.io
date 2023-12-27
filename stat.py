import re
import os
import pandas as pd
import click


def load(filename):
    with open(filename, 'r') as fp:
        content = fp.read()

    title = re.search(r"^title: (.+)$", content, re.MULTILINE)[1]
    opening = content.find('---')
    closing = content.find('---', opening + 1)
    content = content[closing + len('---'):]
    content = content.strip()
    return title, content

def load_all(dir):
    paths = os.walk(dir, followlinks=False)
    files = []
    for path in paths:
        for file_name in path[2]:
            files.append(os.path.join(path[0], file_name))

    # only hard links
    files = [file for file in files if not os.path.islink(file)]

    # filter only markdown
    files = [file for file in files if os.path.splitext(file)[-1].lower() == '.md']
    return [*map(load, files)]

@click.command()
@click.argument('dir', type=click.Path(exists=True, resolve_path=True, file_okay=False))
def stat(dir):
    contents = load_all(dir)
    print(f"Total {len(contents)} contents")
    df = pd.DataFrame(data=contents, columns=['title', 'content'])
    df['words'] = df.apply(lambda row: len(row['content']), axis=1)
    print(df.describe())

if __name__ == '__main__':
    stat()
