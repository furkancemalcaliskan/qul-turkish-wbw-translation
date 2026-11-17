# Changelog

## v1.0.0 — 2026-11-17

Initial reviewed release of `qul-turkish-wbw-translation`, prepared for public
inspection and a future maintainer-coordinated contribution to QUL resource #99.

- Complete the Turkish reference key set: 83,665 locations, including 6,236
  unchanged ayah-number markers, in the supplied English reference order.
- Review the initial 831 flagged constructions against immutable Arabic and
  English sources; retain explicit reasons and interpretive limitations.
- Correct recorded spelling/grammar issues and represent combined Turkish
  expressions with complementary parentheses; exclude square delimiters.
- Preserve all six original QUL files byte-for-byte, with a fixed hash manifest.
- Provide minified UTF-8 JSON and equivalent SQLite with the original QUL schema.
- Keep the root Turkish JSON readable, maintain an equivalent root database,
  and read English directly from the immutable resource.
- Consolidate review evidence into four reports, with reproducible validation,
  release checksums and CI packaging.

External contributions are closed. This release is an independent correction
project, not a QUL-approved publication or independent expert certification.
The source licence information remains unresolved as documented in README.md.
