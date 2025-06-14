# Conc


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Introduction to Conc

Conc is a Python library that brings corpus linguistic analysis to
[Jupyter notebooks](https://docs.jupyter.org/en/latest/). Conc aims to
allow researchers to analyse large corpora in efficient ways using
standard hardware, with the ability to produce clear, publication-ready
reports and extend analysis where required using standard Python
libraries.

A staple of data science, [Jupyter notebooks allow researchers to
present their analysis in an interactive form that combines code,
reporting and
discussion](https://docs.jupyter.org/en/latest/#what-is-a-notebook).
They are an ideal format for collaborating with other researchers during
research or to share analysis in a way others can reproduce and interact
with.

Conc uses [spaCy](https://spacy.io/) for tokenising texts. SpaCy
functionality to annotate texts will be supported soon.

### Conc Principles

- use standard Python libraries for data processing, analysis and
  visualisation (i.e. [Numpy](https://numpy.org/),
  [Scipy](https://scipy.org/), [Polars](https://pola.rs),
  [Plotly](https://plotly.com/python/))
- use fast code libraries (i.e. Conc uses [Polars vs
  Pandas](https://pola.rs/posts/benchmarks/)) and fast data structures
  (e.g. Numpy arrays, columnar data stores)  
- provide clear and complete information when reporting results  
- pre-compute time-intensive and repeatedly used views of the data  
- work with smaller slices of the data where possible  
- cache specific anaysis during a session to reduce computation for
  repeated calls  
- [document corpus representations so that they can be worked with
  directly](https://geoffford.nz/conc/explanations/anatomy.html)  
- [allow researchers to work with Conc results and extend analysis using
  other Python libraries (e.g. output Pandas
  dataframes)](https://geoffford.nz/conc/tutorials/recipes.html)  
- make use of meta-data to allow within-corpus comparisons and to
  provide context for analysis

## Table of Contents

- [Acknowledgements](#acknowledgements)  
- [Development Status](#development-status)  
- [Installation](#installation)
  - [Install via pip](#install-via-pip)  
  - [Install a spaCy model for
    tokenization](#install-a-spacy-model-for-tokenization)  
  - [Install optional dependencies](#install-optional-dependencies)  
  - [Pre-2013 CPU? Install Polars with support for older
    machines](#pre-2013-cpu-install-polars-with-support-for-older-machines)  
- [Using Conc](#using-conc)
  - [Getting Started](https://geoffford.nz/conc/tutorials/start.html)  
  - [Conc Documentation](#conc-documentation)
    - [Tutorials](https://geoffford.nz/conc/tutorials) (Tutorials to get
      you started with Conc)  
    - [Explanations](https://geoffford.nz/conc/explanations) (How Conc
      works, working with Conc corpus formats and results using other
      Python libraries)  
    - [Conc API](https://geoffford.nz/conc/api) (Detailed documentation
      of Conc classes and functions)  
    - [Development](https://geoffford.nz/conc/development) (Information
      on Conc development, including a Roadmap and Developer’s Guide)

## Acknowledgements

Conc is developed by [Dr Geoff Ford](https://geoffford.nz/).

Conc originated in my PhD research, which included development of a
web-based corpus browser to handle analysis of large corpora. I’ve been
developing Conc through my subsequent research.

Work to create this Python library has been made possible by
funding/support from:

- “Mapping LAWS: Issue Mapping and Analyzing the Lethal Autonomous
  Weapons Debate” (Royal Society of New Zealand’s Marsden Fund Grant
  19-UOC-068)  
- “Into the Deep: Analysing the Actors and Controversies Driving the
  Adoption of the World’s First Deep Sea Mining Governance” (Royal
  Society of New Zealand’s Marsden Fund Grant 22-UOC-059)
- Sabbatical, University of Canterbury, Semester 1 2025.

Thanks to the Mapping LAWS project team for their support and feedback
as first users of ConText (a web-based application built on an earlier
version of Conc).

Dr Ford is a researcher with [Te Pokapū Aronui ā-Matihiko \| UC Arts
Digital Lab (ADL)](https://artsdigitallab.canterbury.ac.nz/). Thanks to
the ADL team and the ongoing support of the University of Canterbury’s
Faculty of Arts who make work like this possible.

Thanks to Dr Chris Thomson and Karin Stahel for their feedback on early
versions of Conc.

## Development Status

Conc is in active development. It is currently
[released](https://pypi.org/project/conc/) for beta testing.

Although this is a Beta release, I’m currently using it for research and
postgraduate teaching. I’m keen to support new users. If you have any
questions, hurdles using Conc or feature requests, [create an
issue](https://github.com/polsci/conc/issues/new).

The Github site may be ahead of the Pypi version, so for latest
functionality install from Github (see below). The Github code is
pre-release and may change. For the latest release, install from Pypi
(`pip install conc`). The [documentation](https://geoffford.nz/conc/)
reflects the most recent functionality. See the
[CHANGELOG](https://github.com/polsci/conc/blob/main/CHANGELOG.md) for
notes on releases and the
[Roadmap](https://geoffford.nz/development/roadmap.html) for planned
updates.

## Installation

### Install via pip

You can install Conc from [pypi](https://pypi.org/project/conc/) using
this command:

``` sh
$ pip install conc
```

Add the `-U` flag to upgrade if you are already running Conc.

To install the latest development version of Conc, which may be ahead of
the version on Pypi, you can install from the
[repository](https://github.com/polsci/conc):

``` sh
$ pip install git+https://github.com/polsci/conc.git
```

### Install a spaCy model for tokenization

The first releases of Conc require a SpaCy language model for
tokenization. After installing Conc, install a model. Here’s an example
of how to install SpaCy’s small English model, which is Conc’s default
language model:

``` sh
python -m spacy download en_core_web_sm
```

If you are working with a different language or want to use a different
‘en’ model, check the [SpaCy models
documentation](https://spacy.io/models/) for the relevant model name.

### Install optional dependencies

Conc has some optional dependencies you can install to download source
texts to create sample corpora. These are primarily intended for
creating corpora for development. To minimize Conc’s requirements these
are not installed by default. If you want to get sample corpora to test
out Conc’s functionality you can install these with the following
command.

``` sh
$ pip install nltk requests datasets
```

### Pre-2013 CPU? Install Polars with support for older machines

Polars is optimized for modern CPUs with support for AVX2 instructions.
If you get kernel crashes running Conc on an older machine (probably
pre-2013), this is likely to be an issue with Polars. Polars has an
[alternate installation option to support older
machines](https://docs.pola.rs/user-guide/installation/), which installs
a Polars build compiled without AVX2 support. Replace the standard
Polars package with the legacy-support package to use Conc on older
machines.

``` sh
$ pip uninstall polars
$ pip install polars-lts-cpu
```

## Using Conc

### Getting started

A good place to start is the [Get started with
Conc](https://geoffford.nz/conc/tutorials/start.html) tutorial, which
demonstrates how to build a corpus and output Conc reports. There are
also [simple code
recipes](https://geoffford.nz/conc/tutorials/recipes.html) for common
Conc taks.

### Conc Documentation

There is a dedicated [Conc documentation
site](https://geoffford.nz/conc/). This includes tutorials, examples
demonstrating how to create reports for analysis, explanation of Conc
functionality and its Corpus format, and a reference to Conc’s classes
and methods. Here are links to the documentation site sections:

- [Tutorials](https://geoffford.nz/conc/tutorials) (Tutorials to get you
  started with Conc)  
- [Explanations](https://geoffford.nz/conc/explanations) (How Conc
  works, working with Conc corpus formats and results using other Python
  libraries)  
- [Conc API](https://geoffford.nz/conc/api) (Detailed documentation of
  Conc classes and functions)  
- [Development](https://geoffford.nz/conc/development) (Information on
  Conc development, including a Roadmap and Developer’s Guide)
