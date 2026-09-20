# Changelog of FaSt_Fig

## [0.8.4] - 2026-09-20

- Add title argument to FFig, applied by save() and show()
- Add PyPI publish pipeline with trusted publishing
- Align packaging with the Python Packaging User Guide (explicit build-system, drop stdlib-shadowing dependencies, add project URLs and classifiers)
- Update GitHub Actions to Node 24 runtime

## [0.8.3] - 2026-09-14

- Improve typing for array-like arguments
- set_ylim and set_ylim with finite limits

## [0.8.2] - 2026-04-19

- Add __repr__ and __str__ methods
- Add get_all_labels
- Improve test coverage

## [0.8.0] - 2025-08-28

- Improve figure handling without number
- Plot with list/tuple of vectors

## [0.6.1] - 2025-06-06

- Show with default block=False

## [0.6] - 2025-01-26

- Automatically pass matplotlib methods by __getattr__

## [0.5.3] - 2024-07-04

- Finalize migration to pathlib
- Fix relative import

## [0.5.2] - 2024-06-23

- Implement pylint and ruff warnings
- Add type annotations
- Add logging

## [0.5.1] - 2024-03-28

- Rename class to FFig

## [0.5] - 2024-03-26

- FaSt_Fig initial release, based on classfig
