# Rick and Morty Automation

A Python automation project combining the Rick and Morty REST API, Selenium/Chrome UI
automation, and pytest. It selects an episode and two of its characters, validates
their data, writes character introductions, and searches Google Images for each
character.

## Prerequisites

- Python 3.10 or newer
- Google Chrome
- Internet access to the Rick and Morty API and Google

Selenium Manager resolves a compatible ChromeDriver automatically; a separate
ChromeDriver installation is not normally needed.

## Installation

From the project root, create and activate a virtual environment, then install the
dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, run the interpreter directly as
`.venv\Scripts\python.exe`.

## Running the tests

Run the complete suite:

```powershell
python -m pytest
```

The suite includes unit tests, API tests, and live Google UI tests. To run individual
groups:

```powershell
python -m pytest -m unit
python -m pytest -m api
python -m pytest -m ui
```

API and UI tests require internet access. UI tests open Chrome; Google may show a
CAPTCHA, in which case the test waits for a human to solve it (120 seconds by
default). Use a visible browser for this workflow. A persistent Chrome profile can
preserve consent and other browser state between runs.

The pytest session selects one episode and two characters and shares that selection
between API and UI tests. The selection is random by default. To reproduce a run,
pass a seed; pytest logs the generated seed when one is not supplied:

```powershell
python -m pytest --seed 12345
```

Add `-s` to display the selected episode and character/location messages directly
in the terminal. Pytest also writes an HTML report to `output/report.html` and a
debug log to `output/test_run.log`.

## What the project does

- Fetches all episode pages from the API, randomly chooses an episode with at least
  30 characters, and fetches two distinct characters in one batch request.
- Models API data as `Episode` and `Character` objects.
- Writes each selected character's introduction to
  `output/characters_introduction.txt`.
- Checks character data and compares the selected characters' current locations.
- Opens Google Images through Google's home page, searches for each selected
  character, and saves a screenshot of the selected image element as a timestamped
  JPG under `output/screenshots/`.
- Implements Component A (sort two numbers) and Component B (sort four numbers
  using Component A) in `src/components/sorting.py`.

Generated reports, logs, introductions, screenshots, and failure screenshots are
written under `output/` and are excluded from Git by default.

## Configuration

Settings can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `RM_BASE_URL` | `https://rickandmortyapi.com/api` | API base URL |
| `RM_REQUEST_TIMEOUT` | `10` | API request timeout in seconds |
| `RM_MIN_EPISODE_CHARACTERS` | `30` | Minimum episode character count |
| `RM_GOOGLE_URL` | `https://www.google.com/?hl=en` | Google entry URL |
| `RM_BROWSER_LANGUAGE` | `en` | Chrome language |
| `RM_HEADLESS` | `false` | Start Chrome headless by default |
| `RM_UI_TIMEOUT` | `15` | Selenium explicit-wait timeout in seconds |
| `RM_CAPTCHA_WAIT` | `120` | Seconds to wait for a human to solve a CAPTCHA; `0` fails immediately |
| `RM_CHROME_ARGS` | empty | Additional Chrome command-line arguments |
| `RM_CHROME_PROFILE_DIR` | unset | Chrome profile directory for persistent browser state |
| `RM_OUTPUT_DIR` | `output/` | Directory for generated files |
| `RM_SEED` | unset | Random-selection seed; can also be set with `--seed` |

For example, in PowerShell:

```powershell
$env:RM_CAPTCHA_WAIT = "240"
$env:RM_CHROME_PROFILE_DIR = "$PWD\.chrome-profile"
python -m pytest -m ui
```

## Assumptions and limitations

- The location check follows the assignment's requested assertion: it expects the
  two randomly selected characters to share a location. Since random characters
  often have different locations, `test_characters_share_location` can fail even
  when the API and comparison logic work correctly. The failure message identifies
  both characters and their locations.
- A location named `unknown` is compared by its name like any other location.
- Google controls its markup and may change selectors, show consent dialogs, or
  block automated traffic with a CAPTCHA. The page objects use explicit waits and
  handle the current consent/CAPTCHA flows, but external site changes can still
  require maintenance.
- The image-position rule is applied to the character ID as described in the
  assignment. For IDs with four or more digits, the implementation uses the
  hundreds digit and ones digit; this case is not defined by the assignment.
- UI tests use live Google results, so image ordering and availability can vary.