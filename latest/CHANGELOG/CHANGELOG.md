# Changelog

## [v0.6.0.dev0](https://github.com/SINTEF/oteapi-optimade/tree/v0.6.0.dev0) (2024-09-04)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.5.1...v0.6.0.dev0)

## Support modern session handling in OTEAPI Core

From OTEAPI Core v0.7.0, sessions are handled differently in strategies, leading to signature changes in the strategy methods.
This development release version matches the current development release version(s) of OTEAPI Core (and OTELib).

### Single entity OPTIMADE Structure Resource

A single entity has been added to parse an OPTIMADE Structure resource.
The DLite parse strategy has been updated to support this new entity.

Furthermore, utility/helper functions to parse the resulting `species` and `assemblies` data are available at `oteapi_optimade.parse_species()` and `oteapi_optimade.parse_assemblies()`, respectively.

### DX updates

The permanent dependencies branch has been removed in favor of using Dependabot's groups feature and merging everything directly into `main`.

**Implemented enhancements:**

- Stop using the permanent dependencies branch [\#254](https://github.com/SINTEF/oteapi-optimade/issues/254)
- Support new OTEAPI session handling [\#213](https://github.com/SINTEF/oteapi-optimade/issues/213)
- Minimize SOFT data model to a single file [\#195](https://github.com/SINTEF/oteapi-optimade/issues/195)

**Merged pull requests:**

- Use proper packages [\#258](https://github.com/SINTEF/oteapi-optimade/pull/258) ([CasperWA](https://github.com/CasperWA))
- Remove everything to do with the permanent dependencies branch [\#255](https://github.com/SINTEF/oteapi-optimade/pull/255) ([CasperWA](https://github.com/CasperWA))
- Support OTEAPI Core v0.7 [\#236](https://github.com/SINTEF/oteapi-optimade/pull/236) ([CasperWA](https://github.com/CasperWA))
- Single SOFT entity for structure resource [\#196](https://github.com/SINTEF/oteapi-optimade/pull/196) ([CasperWA](https://github.com/CasperWA))

## [v0.5.1](https://github.com/SINTEF/oteapi-optimade/tree/v0.5.1) (2024-09-03)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.5.0...v0.5.1)

## Update to latest dependencies

Update dependencies to support the latest core libraries.

This release is done almost immediately prior to the v0.6.0.dev0 release, which will support the upcoming re-design of OTEAPI Core and the use of sessions.

**Fixed bugs:**

- Use Trusted Publishers with PyPI [\#252](https://github.com/SINTEF/oteapi-optimade/issues/252)

**Merged pull requests:**

- Use Trusted Publishers for publishing on PyPI [\#253](https://github.com/SINTEF/oteapi-optimade/pull/253) ([CasperWA](https://github.com/CasperWA))

## [v0.5.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.5.0) (2024-03-07)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.4.2...v0.5.0)

**Implemented enhancements:**

- Migrate to pydantic v2 [\#163](https://github.com/SINTEF/oteapi-optimade/issues/163)

**Fixed bugs:**

- Pin to specific `oteapi` docker image version for testing [\#187](https://github.com/SINTEF/oteapi-optimade/issues/187)

**Merged pull requests:**

- Pin oteapi docker image to pre-pydantic v2 [\#188](https://github.com/SINTEF/oteapi-optimade/pull/188) ([CasperWA](https://github.com/CasperWA))
- Upgrade ruff rules and more [\#183](https://github.com/SINTEF/oteapi-optimade/pull/183) ([CasperWA](https://github.com/CasperWA))
- Migrate to pydantic v2 [\#182](https://github.com/SINTEF/oteapi-optimade/pull/182) ([CasperWA](https://github.com/CasperWA))

## [v0.4.2](https://github.com/SINTEF/oteapi-optimade/tree/v0.4.2) (2023-10-26)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.4.1...v0.4.2)

## [v0.4.1](https://github.com/SINTEF/oteapi-optimade/tree/v0.4.1) (2023-10-26)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.4.0...v0.4.1)

**Fixed bugs:**

- Invalid use of logging [\#174](https://github.com/SINTEF/oteapi-optimade/issues/174)
- OPTIMADE plugin produces empty instances of http://onto-ns.com/meta/1.0/OPTIMADEStructureSpecies  [\#162](https://github.com/SINTEF/oteapi-optimade/issues/162)

**Merged pull requests:**

- Properly create assemblies and species [\#172](https://github.com/SINTEF/oteapi-optimade/pull/172) ([CasperWA](https://github.com/CasperWA))
- Proper use of logging [\#171](https://github.com/SINTEF/oteapi-optimade/pull/171) ([jesper-friis](https://github.com/jesper-friis))

## [v0.4.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.4.0) (2023-10-23)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.3.0...v0.4.0)

**Implemented enhancements:**

- Add example\(s\) [\#124](https://github.com/SINTEF/oteapi-optimade/issues/124)

**Fixed bugs:**

- Wrong OPTIMADEStructureAttributes datamodel [\#164](https://github.com/SINTEF/oteapi-optimade/issues/164)
- Pipeline figure not being shown in docs [\#144](https://github.com/SINTEF/oteapi-optimade/issues/144)
- Updated DLite installation pathway [\#136](https://github.com/SINTEF/oteapi-optimade/issues/136)
- `Segmentation fault` from dlite in CI [\#115](https://github.com/SINTEF/oteapi-optimade/issues/115)
- init file missing in the new `dlite` module [\#113](https://github.com/SINTEF/oteapi-optimade/issues/113)

**Closed issues:**

- Make the JSON-serialisation of entities human readable [\#160](https://github.com/SINTEF/oteapi-optimade/issues/160)
- Use ruff instead of pylint \(and isort\) [\#156](https://github.com/SINTEF/oteapi-optimade/issues/156)

**Merged pull requests:**

- Write Ångström such that it is understandable by Pint in datamodel [\#170](https://github.com/SINTEF/oteapi-optimade/pull/170) ([jesper-friis](https://github.com/jesper-friis))
- Update data models [\#169](https://github.com/SINTEF/oteapi-optimade/pull/169) ([CasperWA](https://github.com/CasperWA))
- Move from pylint \(& isort\) to ruff [\#157](https://github.com/SINTEF/oteapi-optimade/pull/157) ([CasperWA](https://github.com/CasperWA))
- Use relative link, which works only in production [\#145](https://github.com/SINTEF/oteapi-optimade/pull/145) ([CasperWA](https://github.com/CasperWA))
- Avoid DLite v0.4.0 [\#139](https://github.com/SINTEF/oteapi-optimade/pull/139) ([CasperWA](https://github.com/CasperWA))
- DLite notebook example [\#127](https://github.com/SINTEF/oteapi-optimade/pull/127) ([CasperWA](https://github.com/CasperWA))
- Add example to documentation [\#125](https://github.com/SINTEF/oteapi-optimade/pull/125) ([CasperWA](https://github.com/CasperWA))
- Add \_\_init\_\_ file to dlite submodule [\#122](https://github.com/SINTEF/oteapi-optimade/pull/122) ([CasperWA](https://github.com/CasperWA))
- Avoid psycopg2-binary v2.9.6 [\#117](https://github.com/SINTEF/oteapi-optimade/pull/117) ([CasperWA](https://github.com/CasperWA))

## [v0.3.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.3.0) (2023-03-30)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.2.2...v0.3.0)

**Implemented enhancements:**

- Use `SINTEF/ci-cd` CI - Tests workflow [\#71](https://github.com/SINTEF/oteapi-optimade/issues/71)
- Implement support for DLite [\#31](https://github.com/SINTEF/oteapi-optimade/issues/31)

**Fixed bugs:**

- Fix CI/CD workflows for external usage [\#84](https://github.com/SINTEF/oteapi-optimade/issues/84)
- Update to `SINTEF/ci-cd` instead of `CasperWA/ci-cd` [\#72](https://github.com/SINTEF/oteapi-optimade/issues/72)

**Closed issues:**

- Use SINTEF/ci-cd v2 [\#104](https://github.com/SINTEF/oteapi-optimade/issues/104)
- Reinstate pre-commit hooks for docs [\#68](https://github.com/SINTEF/oteapi-optimade/issues/68)

**Merged pull requests:**

- Support DLite [\#109](https://github.com/SINTEF/oteapi-optimade/pull/109) ([CasperWA](https://github.com/CasperWA))
- Update to SINTEF/ci-cd v2 [\#105](https://github.com/SINTEF/oteapi-optimade/pull/105) ([CasperWA](https://github.com/CasperWA))
- Update input keywords for SINTEF/ci-cd workflows [\#85](https://github.com/SINTEF/oteapi-optimade/pull/85) ([CasperWA](https://github.com/CasperWA))
- Use CasperWA/ci-cd pre-commit hooks [\#69](https://github.com/SINTEF/oteapi-optimade/pull/69) ([CasperWA](https://github.com/CasperWA))

## [v0.2.2](https://github.com/SINTEF/oteapi-optimade/tree/v0.2.2) (2022-07-06)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.2.1...v0.2.2)

**Implemented enhancements:**

- Update to use all workflows from CasperWA/gh-actions [\#63](https://github.com/SINTEF/oteapi-optimade/pull/63) ([CasperWA](https://github.com/CasperWA))

**Fixed bugs:**

- New workflow is removing API reference in documentation [\#64](https://github.com/SINTEF/oteapi-optimade/issues/64)

**Closed issues:**

- Update to new repository name for callable workflows [\#66](https://github.com/SINTEF/oteapi-optimade/issues/66)

**Merged pull requests:**

- Use new repo name for callable workflows repo [\#67](https://github.com/SINTEF/oteapi-optimade/pull/67) ([CasperWA](https://github.com/CasperWA))
- Properly create API reference and clean up [\#65](https://github.com/SINTEF/oteapi-optimade/pull/65) ([CasperWA](https://github.com/CasperWA))

## [v0.2.1](https://github.com/SINTEF/oteapi-optimade/tree/v0.2.1) (2022-07-01)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.2.1-alpha.1...v0.2.1)

**Closed issues:**

- Set `test: false` for publish workflow [\#61](https://github.com/SINTEF/oteapi-optimade/issues/61)

**Merged pull requests:**

- Don't run publish workflow as a test [\#62](https://github.com/SINTEF/oteapi-optimade/pull/62) ([CasperWA](https://github.com/CasperWA))

## [v0.2.1-alpha.1](https://github.com/SINTEF/oteapi-optimade/tree/v0.2.1-alpha.1) (2022-07-01)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.2.0...v0.2.1-alpha.1)

**Implemented enhancements:**

- Auto-merge generated PR from new workflow [\#49](https://github.com/SINTEF/oteapi-optimade/issues/49)
- Properly update dependencies [\#46](https://github.com/SINTEF/oteapi-optimade/issues/46)
- Use CasperWA/gh-actions workflows [\#60](https://github.com/SINTEF/oteapi-optimade/pull/60) ([CasperWA](https://github.com/CasperWA))

**Fixed bugs:**

- New workflow failing [\#48](https://github.com/SINTEF/oteapi-optimade/issues/48)

**Merged pull requests:**

- \[Auto-generated\] Update dependencies [\#53](https://github.com/SINTEF/oteapi-optimade/pull/53) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#52](https://github.com/SINTEF/oteapi-optimade/pull/52) ([TEAM4-0](https://github.com/TEAM4-0))
- Auto-merge new CD workflow-generated PR [\#50](https://github.com/SINTEF/oteapi-optimade/pull/50) ([CasperWA](https://github.com/CasperWA))
- New CD workflow to update dependencies in pyproject.toml [\#47](https://github.com/SINTEF/oteapi-optimade/pull/47) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#44](https://github.com/SINTEF/oteapi-optimade/pull/44) ([TEAM4-0](https://github.com/TEAM4-0))

## [v0.2.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.2.0) (2022-05-18)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.1.0...v0.2.0)

**Implemented enhancements:**

- Implement OPTIMADE filter strategy [\#4](https://github.com/SINTEF/oteapi-optimade/issues/4)

**Fixed bugs:**

- CI docker connection issues [\#34](https://github.com/SINTEF/oteapi-optimade/issues/34)

**Closed issues:**

- Use the `optimade` container image in CI [\#41](https://github.com/SINTEF/oteapi-optimade/issues/41)
- Extend acknowledgements in README [\#38](https://github.com/SINTEF/oteapi-optimade/issues/38)

**Merged pull requests:**

- Use the optimade container image in CI [\#42](https://github.com/SINTEF/oteapi-optimade/pull/42) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#40](https://github.com/SINTEF/oteapi-optimade/pull/40) ([TEAM4-0](https://github.com/TEAM4-0))
- Add VIPCOAT and OpenModel to README ack [\#39](https://github.com/SINTEF/oteapi-optimade/pull/39) ([CasperWA](https://github.com/CasperWA))
- Fix real backend CI job [\#37](https://github.com/SINTEF/oteapi-optimade/pull/37) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#36](https://github.com/SINTEF/oteapi-optimade/pull/36) ([TEAM4-0](https://github.com/TEAM4-0))
- Add a Filter strategy [\#33](https://github.com/SINTEF/oteapi-optimade/pull/33) ([CasperWA](https://github.com/CasperWA))

## [v0.1.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.1.0) (2022-03-29)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.0.2...v0.1.0)

**Implemented enhancements:**

- Correctly handle trailing slashes \(`/`\) [\#28](https://github.com/SINTEF/oteapi-optimade/issues/28)

**Merged pull requests:**

- Trailing slash in base URL [\#29](https://github.com/SINTEF/oteapi-optimade/pull/29) ([CasperWA](https://github.com/CasperWA))

## [v0.0.2](https://github.com/SINTEF/oteapi-optimade/tree/v0.0.2) (2022-03-29)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/b90d7c4bd5b8c5cfee08fd76dae3240c1e5955e9...v0.0.2)

**Implemented enhancements:**

- Implement OPTIMADE parse strategy [\#5](https://github.com/SINTEF/oteapi-optimade/issues/5)
- Implement OPTIMADE resource strategy [\#3](https://github.com/SINTEF/oteapi-optimade/issues/3)

**Fixed bugs:**

- Fix CI connection refusal for pytest-real-backend job [\#26](https://github.com/SINTEF/oteapi-optimade/issues/26)
- CD workflow failing - flit not building [\#23](https://github.com/SINTEF/oteapi-optimade/issues/23)
- Black issue with click [\#21](https://github.com/SINTEF/oteapi-optimade/issues/21)
- CD workflow failing [\#18](https://github.com/SINTEF/oteapi-optimade/issues/18)
- GH GraphQL type issue in auto-merge workflow [\#6](https://github.com/SINTEF/oteapi-optimade/issues/6)
- Fix CI [\#1](https://github.com/SINTEF/oteapi-optimade/issues/1)

**Closed issues:**

- CI test with end-to-end [\#17](https://github.com/SINTEF/oteapi-optimade/issues/17)

**Merged pull requests:**

- Fix pytest-real-backend CI job [\#27](https://github.com/SINTEF/oteapi-optimade/pull/27) ([CasperWA](https://github.com/CasperWA))
- Test release workflow [\#25](https://github.com/SINTEF/oteapi-optimade/pull/25) ([CasperWA](https://github.com/CasperWA))
- Build package prior to polluting git tree [\#24](https://github.com/SINTEF/oteapi-optimade/pull/24) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit hooks [\#22](https://github.com/SINTEF/oteapi-optimade/pull/22) ([CasperWA](https://github.com/CasperWA))
- Fix failing release workflow [\#20](https://github.com/SINTEF/oteapi-optimade/pull/20) ([CasperWA](https://github.com/CasperWA))
- Setup CI end-to-end test [\#19](https://github.com/SINTEF/oteapi-optimade/pull/19) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#15](https://github.com/SINTEF/oteapi-optimade/pull/15) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#13](https://github.com/SINTEF/oteapi-optimade/pull/13) ([TEAM4-0](https://github.com/TEAM4-0))
- Implement an OPTIMADE Resource strategy [\#12](https://github.com/SINTEF/oteapi-optimade/pull/12) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#11](https://github.com/SINTEF/oteapi-optimade/pull/11) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#10](https://github.com/SINTEF/oteapi-optimade/pull/10) ([TEAM4-0](https://github.com/TEAM4-0))
- Use `ID!` type instead of `String!` [\#7](https://github.com/SINTEF/oteapi-optimade/pull/7) ([CasperWA](https://github.com/CasperWA))
- Fix CI and use flit [\#2](https://github.com/SINTEF/oteapi-optimade/pull/2) ([CasperWA](https://github.com/CasperWA))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
