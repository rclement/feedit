# Feedit

> Generate static RSS/Atom feeds for websites without it.
> "Just feed-it!"

[![CI/CD](https://github.com/rclement/feedit/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/rclement/feedit/actions/workflows/ci-cd.yml)
[![Schedule](https://github.com/rclement/feedit/actions/workflows/schedule.yml/badge.svg)](https://github.com/rclement/feedit/actions/workflows/schedule.yml)

## Usage

```bash
python -m feedit.main fetch --output feeds
```

## Development

### Python environment

```
pipenv install -d
pipenv run inv qa
```

### VSCode

If using VSCode, use the following configuration in `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Module",
      "type": "python",
      "request": "launch",
      "module": "feedit.main",
      "args": ["fetch", "--output", "feeds"],
      "justMyCode": false
    },
    {
      "name": "tests",
      "type": "python",
      "request": "test",
      "justMyCode": false,
      "env": {
        "CI": "false"
      }
    }
  ]
}
```

## Inspiration

- https://github.com/RSS-Bridge/rss-bridge
- https://github.com/damoeb/rss-proxy
- https://github.com/qsniyg/rssit
- https://github.com/DIYgod/RSSHub

## License

Licensed under GNU Affero General Public License v3.0 (AGPLv3)

Copyright (c) 2022 - present Romain Clement
