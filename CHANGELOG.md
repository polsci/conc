# Change log

## [0.1.2] - 2025-06-12 - CI build improvements and new corpora module

### Added

- exposed concordance plot via Conc interface class
- added conc.corpora module
- added console script conc_build_sample_corpora to be used in CI
- added anywidget dependency for concordance plot

### Changed

- moved build_test_corpora from conc.core to conc.corpora as build_sample_corpora
- raise depreciation error for build_test_corpora
- move function from conc.core related to corpus source downloads to conc.corpora
- depreciated calls in conc.core log warnings and run new functions in conc.corpora
- changed CI workflow to use conc_build_sample_corpora

### Fixed

- resolve error related to column not found when changing concordance context lengths

## [0.1.1] - 2025-06-10

### Fixed

- move memory_profiler from dev to main dependencies

### [0.1.0] - 2025-06-09

Initial release of Conc
