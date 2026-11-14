# env-assert (Python)

Assert required environment variables with clear, aggregated errors.

Zero dependencies. Companion to the Node package [`env-assert`](https://github.com/olimasad/env-assert).

## Install

```bash
pip install env-assert
```

## Usage

```python
from env_assert import assert_env

env = assert_env({
    "PORT": {"type": "int", "min": 1, "max": 65535, "default": 3000},
    "DATABASE_URL": {"type": "url"},
    "DEBUG": {"type": "bool", "default": False},
})
```

## License

MIT © Oliver Massaad
