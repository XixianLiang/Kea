# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../../../'))
language = os.getenv('LANGUAGE', 'zh')
# -- Project information

project = "Kea"
copyright = "2024, ECNU-SE-lab"
author = "梁锡贤、沈祥臣、马搏、熊一衡"

release = "2.0.3"
version = "1.0"

locale_dirs = ['locales/']  # 翻译文件目录
gettext_compact = False
language = 'zh-CN'  # 默认语言

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"

pygments_style = "sphinx"

latex_engine = "xelatex"
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "preamble": r"""
\usepackage{xeCJK}
\setCJKmainfont[BoldFont=STZhongsong, ItalicFont=STKaiti]{STSong}
\setCJKsansfont[BoldFont=STHeiti]{STXihei}
\setCJKmonofont{STFangsong}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt
\parindent 2em
\definecolor{VerbatimColor}{rgb}{0.95,0.95,0.95}
\setcounter{tocdepth}{3}
\renewcommand\familydefault{\ttdefault}
\renewcommand\CJKfamilydefault{\CJKrmdefault}
""",
}
