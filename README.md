# Investigation Skills

Three agent skills for investigating visual clues, recovering internet history, and checking claims against evidence.

Each skill combines a research workflow with Python utilities, reference material, report templates, and tests. Built for Codex, the collection helps turn incomplete clues into sourced findings with explicit uncertainty.

## The collection

| Skill | What it investigates | Guide |
| --- | --- | --- |
| **Sherlock Investigator** | Capture locations, GeoGuessr-style coordinates, object models, and media provenance from visual clues | [Documentation](skills/sherlock-investigator/README.md) |
| **Internet Archaeologist** | Lost websites, forgotten games, abandoned software, renamed projects, and historical changes | [Documentation](skills/internet-archaeologist/README.md) |
| **Truth Engine** | Original sources, numerical accuracy, contradictory evidence, and the context behind circulating media | [Documentation](skills/truth-engine/README.md) |

The workflows emphasize source provenance, competing explanations, and checks for contradictory evidence. Reports distinguish observations from interpretations and identify what remains unverified.

## Quick start

Requires **Python 3.11+**, **Git**, and a Codex environment with skill support.

```sh
git clone https://github.com/littledumhung/investigation-skills.git
cd investigation-skills
python -m pip install -r requirements.txt
python tools/install_skills.py
```

The installer copies all three skills into `$CODEX_HOME/skills`, or `~/.codex/skills` when `CODEX_HOME` is unset. Open a new Codex conversation after installation.

Existing skill folders are never overwritten. If a name is already installed, move the existing folder outside the skills directory before installing its replacement.

To preview an installation or choose another destination:

```sh
python tools/install_skills.py --dry-run
python tools/install_skills.py --dest /path/to/skills
```

## Use in Codex

Invoke a skill by name and provide the material you want investigated.

**Investigate an image**

```text
Use $sherlock-investigator to locate the camera position in this GeoGuessr
image. Compare plausible locations and give coordinates, supporting clues,
and an estimated error range.
```

**Find something from the past**

```text
Use $internet-archaeologist to find a browser game I played around 2012.
It had a blue block character and grid-based puzzles. Compare candidates
and link to archived pages that support or rule out each match.
```

**Check a claim**

```text
Use $truth-engine to check this article's claim that a treatment reduces
risk by 40%. Trace the original study, distinguish relative and absolute
risk, and look for evidence that challenges the claim.
```

Skill instructions and supporting documentation are primarily in Traditional Chinese. Request English in your prompt for English responses.

## How it works

The agent handles interpretation, research strategy, source comparison, and conclusions. The Python tools handle deterministic tasks such as hashing media, collecting archive metadata, validating evidence records, performing calculations, and generating reports.

| Capability | Requirement |
| --- | --- |
| Report validation | `jsonschema`, included in `requirements.txt` |
| Local image processing | `Pillow`, included in `requirements.txt` |
| Video frame extraction in Sherlock | `ffmpeg` installed separately and available on `PATH` |
| Web research, maps, street view, OCR, and visual interpretation | Suitable tools available to the host agent |
| Optional search providers | Provider-specific configuration; see each skill's `.env.example` |

The Python CLIs assist investigations; they do not independently perform the agent's semantic reasoning or establish that a claim is true. Installing the collection does not add search, map, or vision services to the host. A separate API key is not required to invoke the skills with the host's existing tools; optional providers may require one.

## Python utilities

Run each CLI from its own skill directory:

```sh
cd skills/truth-engine
python scripts/cli.py --help
```

Each skill includes its own `pyproject.toml`. All three packages currently use the top-level Python module name `scripts`; use a separate virtual environment for each package if installing them with `pip install .` or using their installed command-line entry points. Direct script execution avoids installing those overlapping packages together.

## Development

Install the development dependencies and run the offline validation suite:

```sh
python -m pip install -r requirements-dev.txt
python tools/validate_all.py
```

The validator checks skill metadata and linked resources, then runs each test suite in a separate process. The video extraction test is skipped when `ffmpeg` is unavailable.

[GitHub Actions](https://github.com/littledumhung/investigation-skills/actions) is configured to run validation on Windows and Ubuntu with Python 3.11 and 3.12, including installation of `ffmpeg`.

```text
skills/
  sherlock-investigator/   Visual investigation workflows and media tools
  internet-archaeologist/  Archive research and historical evidence tools
  truth-engine/           Claim verification and evidence reporting tools
tools/
  install_skills.py       Install the collection into a skill directory
  validate_all.py         Validate metadata, resources, and test suites
```

Generated investigation output is excluded from version control. The per-skill `VALIDATION.md` and `VERIFICATION.md` files document earlier validation runs; they are historical records, not live CI status.

## License

[MIT](LICENSE). Each skill retains its own license and copyright notices. Third-party dependencies and external services remain subject to their respective licenses and terms.
