# Reprocess crash reports from Super Search

Reprocessing tool for [Mozilla's crash-stats systems](https://crash-stats.mozilla.com/) (using [Socorro](https://github.com/mozilla/socorro)).

This script pulls a list of crash IDs from a Super Search query and sends them for reprocessing. It takes parameters formatted like ``{key}={value}``, which makes it easy to use and edit.

For example, this:

```bash
./reprocess.py -t authToken product=Firefox version=49.0b0 version=50.0b0 'date=>2016-10-01' 'build_id=>0'
```

... will reprocess all crash reports from Firefox 49.0b0 and Firefox 50.0b0, with a valid build_id and that happened since October 1st, 2016.

## Installation

Clone this repository, ``cd`` into it, then install the dependencies:

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
./reprocess.py --auth-token=XXX key1=value1 key2=value2
```

Options:

```
-t, --auth-token TEXT     An Auth Token that has the "Reprocess Crashes" permission on target environment
-s, --batch-size INTEGER  Number of documents to query or send at once (default: 500)
-e, --env [prod|stage]    Target crash-stats environment (stage or prod) (default: prod)
```
