# run as 
# python scripts/renderpng.py nbs/
# from repo root directory
# looks for cells with #renderpng in the notebook files and renders the following output
# when adding to cell - recommended to #| hide that cell
# add the class after the #renderpng comment to specify a specific target class (e.g. gt_table or conc-plot-wrapper)
# to get this functionality working i've made sure nbconvert is setup with latest dependencies for rendering (see docs)
# also installed playwright - not adding this to dependencies as this is not relevant for tests - just generating the docs
# may change that later
#pip install nbconvert[webpdf]
#playwright install chromium
#jupyter nbconvert --to webpdf 00_nb.ipynb

import argparse
import subprocess
import tempfile
import os
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

def convert_notebook_to_html(notebook_path, html_path):
    """ Use nbconvert to convert notebook to HTML """
    subprocess.run([
        sys.executable, '-m', 'nbconvert',
        '--to', 'html',
        '--output', html_path,
        notebook_path
    ], check=True)

async def screenshot_cells(html_path, output_prefix):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        file_url = f'file://{html_path}'
        await page.goto(file_url)
        
        page_source = await page.content()

        cells = await page.locator('.jp-Cell').all()
        cells = [cell for cell in cells if '#renderpng' in (await cell.inner_text())]
        print(f"Found {len(cells)} cells in the notebook.")
        if not cells:
            print("No cells with '#renderpng' found.")
        for idx, cell in enumerate(cells, 1):
            class_name = (await cell.inner_text()).split('#renderpng')[1].strip().split('\n')[0]

            rendered = cell.locator('.jp-RenderedHTML')

            if class_name != "":
                print(f"Cell {idx} class: {class_name}")
                rendered = rendered.locator(f'.{class_name}')

            if await rendered.count() > 0:
                await rendered.first.screenshot(path=f"{output_prefix}-{idx}.png")
                print(f"Saved: {output_prefix}-{idx}.png")
            else:
                print(f"No .jp-RenderedHTML found in cell {idx}")
        await browser.close()

def main():
    parser = argparse.ArgumentParser(description="Render notebook cells to PNGs.")
    parser.add_argument("path", help="Path to the notebook files")
    args = parser.parse_args()

    notebook_path = Path(args.path).resolve()

    if not notebook_path.is_dir():
        print(f"Provided path is not a directory: {notebook_path}")
        sys.exit(1)

    notebook_files = list(notebook_path.rglob("*.ipynb"))
    if not notebook_files:
        print(f"No notebook files found in directory: {notebook_path}")
        sys.exit(1)

    for notebook_file in notebook_files:
        print(f"Processing notebook: {notebook_file}")

        output_prefix = os.path.join(notebook_path, notebook_file.stem)

        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = Path(tmpdir) / (notebook_file.stem + ".html")
            convert_notebook_to_html(str(notebook_file), str(html_path))
            asyncio.run(screenshot_cells(str(html_path), output_prefix))
        
        if html_path.exists():
            os.remove(html_path)
            print(f"Removed temporary HTML file: {html_path}")

if __name__ == "__main__":
    main()
