# Changelog

## [v0.4.0](https://github.com/SINTEF/oteapi-optimade/tree/v0.4.0) (2023-10-23)

[Full Changelog](https://github.com/SINTEF/oteapi-optimade/compare/v0.3.0...v0.4.0)

**Implemented enhancements:**

- Add example\(s\) [\#124](https://github.com/SINTEF/oteapi-optimade/issues/124)

**Fixed bugs:**

- Wrong OPTIMADEStructureAttributes datamodel [\#164](https://github.com/SINTEF/oteapi-optimade/issues/164)
- OPTIMADE plugin produces empty instances of http://onto-ns.com/meta/1.0/OPTIMADEStructureSpecies  [\#162](https://github.com/SINTEF/oteapi-optimade/issues/162)
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
