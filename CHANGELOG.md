# Change log

This document is based on https://keepachangelog.com/en/1.1.0/ and classifies changes as
Added, Changed, Deprecated, Removed, Fixed, or Security

This information is mirrored on the documentation site [Releases page](https://geoffford.nz/conc/development/releases.html).

## [0.1.8] - 2025-07-10 - bug fix so list corpora ready for use after build

### Fixed

- init the corpus after build so vocab is ready for use

## [0.1.7] - 2025-07-09 - keywords report improvements, BNC XML parsing, lightweight ListCorpus format for reference corpora

### Added

- added BNC xml parsing to conc.corpora
- ListCorpus format - lightweight format with frequency information for use as a reference corpus
- support for ListCorpus added to keywords, raising errors in non-supported report classes
- documented ListCorpus in recipes
- added document frequency reporting to ngram_frequencies
- added optional standardisation of apostrophes when building corpora
- added support to exclude/include negative keywords in keywords report

### Changed

- changed Corpus.build to _build, added flexibility to expected/required files, and improved docs
- stop words via Conc.core are now sorted
- requiring lxml dependency for BNC XML parsing
- keywords report defaults to trying to resolve apostrophe character differences in word tokens
- changed default keywords order to log likelihood

### Fixed

- ensure page size 0 (all data) works in keywords method
- fix issue with 0 frequencies not using observed frequency correction in keywords report

## [0.1.6] - 2025-07-02 - concordance filtering based on context words, improved display of texts

### Added

- added concordancing functionality to allow specifying a context word within a specific span
- new parameters to control reflow and wrapping of text via Text class (or Corpus.text)

### Changed

- tweaks to documentation (recipes) for new functionality in 0.1.5 and 0.1.6
- using ignore punctuation True as default for concordance, so concordance sort defaults to word token sorting

## [0.1.5] - 2025-06-30 - improved concordance sorting, new features to support release of [ConText](https://github.com/polsci/ConText)

### Added

- Corpus.report - allows accessing Corpus summary as a Result object
- added Plot class
- added functionality for auto-calculating ngram_length based on input
- highlighting in text output
- added flag to allow/prevent multiple formats for sample corpora sources
- added MIDDLE ngram_token_position
- support for ignoring punctuation in concordance sorts
- support for scaling of concordance plot
- doc_position_to_corpus_position in Text to allow translating positions

### Changed

- expanded punctuation list to unicode tokens to allow better punctuation token detection
- improve formatting of concordances and other tables
- improved plot rendering to allow multiple concordance plots per page
- revised sample corpora processes to ensure archives compressed, metadata used
- prevented possible many iterations when scanning for sort tokens
- passing doc/offset in svg element attributes (support for ConText clickable plots)

### Fixed

- fix to prevent negative start indexes and associated weirdness

## [0.1.4] - 2025-06-18 - documentation and test improvements, Result/Text class updates

### Added

- added tutorials, recipes, install page and other documentation
- nox-based pre-release test script for Pythons 3.10+
- renderpng.py in scripts to render screenshots for docs
- added Result.to_html method to support Text revisions and more flexible output options

### Changed

- restructured and updated documentation 
- minor code changes related to documentation clarity (e.g. formatting of corpus_path values from build)
- improved Text class HTML output, new functionality in Text to support this
- simplified Result class internal structure for more flexible output

## [0.1.3] - 2025-06-13 - concordance plot improvements

### Changed

- concordance plot rewritten in pure HTML/JS/CSS without Plotly/AnyWidget for better performance and portability across Jupyter environments

### Removed

- AnyWidget dependency (due to rewrite of concordance plot)

## [0.1.2] - 2025-06-12 - CI build improvements and new corpora module

### Added

- exposed concordance plot via Conc interface class
- added conc.corpora module
- added console script conc_build_sample_corpora to be used in CI
- added anywidget dependency for concordance plot

### Changed

- moved build_test_corpora from conc.core to conc.corpora as build_sample_corpora
- raise deprecation error for build_test_corpora
- move function from conc.core related to corpus source downloads to conc.corpora
- deprecated calls in conc.core log warnings and run new functions in conc.corpora
- changed CI workflow to use conc_build_sample_corpora

### Fixed

- resolve error related to column not found when changing concordance context lengths

## [0.1.1] - 2025-06-10 - Dependency fix

### Fixed

- move memory_profiler from dev to main dependencies

## [0.1.0] - 2025-06-09 - Initial release

Initial release of Conc
