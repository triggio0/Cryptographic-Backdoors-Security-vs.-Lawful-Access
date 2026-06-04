# Cybersecurity and National Defence -- Technical Project

## Topic A -- Authorization Policy Engine

---

## Group Members

- Emre Utkueri -- s322401
- Tommaso Riggio -- s336265

---

## Project Description

This project implements a authorization policy engine.

The program receives:
- a list of subjects;
- a list of resources;
- a list of policies;
- a list of requests.

For each request, the program cross-references the 3 input data and decides if the requested action is permitted.

The model uses a default deny model. This means the request is permitted only if at least one policy exactly matches the requirements. If no policy matches, the request is denied.

The program produces a JSON output file containing:
- a summary of the total number of requests;
- the number of permitted and denied requests;
- the matching policy if the request is permitted;
- a summary of the matched conditions.

---

## Project Structure

- `main.py`: main program, reads and evaluates requests
- `loader.py`: helper file used to load JSON files.
- `src/`: Python modules used by the program
- `input/`: input files
- `output/`: output file
- `requirements.txt`: list of required Python libraries
- `README.md`: document explaining the project and design it.
- `requirements.txt`: list of required libraries (Only the Python library is used, so the file is empty.)


---

## Python Version

This project was written for:

Python 3.11
It should also work with any Python 3 versions

---

## Required Libraries

Only the Python library is used, so the file is empty.

---

## Creating a Virtual Environment

A virtual environment is recommended in order to run the project in an isolated way.

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## How to Run the Program

The program can be executed from the command line with:

python main.py --input example_input --output output.json

---

## Input Files

- `subjects.json`: Contains the subjects.

  Each subject has:
    - `id`: unique identifier;
    - `role`: role of the subject;
    - `clearance`: integer clearance level.


- `resources.json`: Contains the resources.

  Each resource has:
    - `id`: unique identifier;
    - `type`: type of resource;
    - `owner`: subject id of the owner;
    - `classification`: classification label.


- `policies.json`: Contains the authorization policies.

  Each policy can contain:
    - `id`: policy identifier;
    - `subject`: conditions on the subject;
    - `resource`: conditions on the resource;
    - `actions`: list of permitted actions;
    - `context`: optional context constraints.


Subject conditions:

- `role`
- `clearance_min`

Resource conditions:

- `type`
- `classification`
- `owner_is_subject`

Context conditions:

- `mfa_required`
- `hour_min`
- `hour_max`


- `requests.json`: Contains the requests to  be evaluated.

  Each request has:
    - `request_id`
    - `subject_id`
    - `resource_id`
    - `action`
    - `context`

---

## Main Lookup Data Structures

The model uses two dictionaries for the lookup operations:

- `subjects_by_id`: Maps each subject's attributes and uses their id as key

Example:
{"u200"} : {"id": "u200", "role": "professor", "clearance": 2}


- `resources_by_id`: Maps each resource's attributes and uses their id as key

Example:
{"e700"} : {"id": "e700", "type": "exam_record", "owner": "u200", "classification": "normal" }


---

## Edge Case Explicitly Handled

An important edge case handled by the model is unknown subjects or resources.

For example, if a request contains a user id not in the `subjects.json` file, the model authomatically denies the request. The same happens if the resource id is unknown.

---

## Limitation of the Design

The model supports only permit policies. There are no deny policies.

To represent this type of logic, the main file would need a priority logic between permit and deny policies.
