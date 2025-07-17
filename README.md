pyozo
=====

`pyozo` is a pure-Python communication library and a tool for exploring the hardware and software of [Ozobot](https://ozobot.com/) robots.

It is unstable and heavily under development.


Usage
-----

```python
import asyncio
import pyozo


async def main():
    async with pyozo.get_robot() as robot:
        name = await robot.get_name()
        print(f"Hello {name}!")


asyncio.run(main())
```


Requirements
------------

- [Python](https://www.python.org/downloads/) 3.11 or newer
- [Bleak](https://github.com/hbldh/bleak) - a cross-blatform Bluetooth LE client library
- Ozobot Evo firmware 3.x.x


Installation
------------

Using pip:

```
pip install pyozo
```

From source:

```
git clone https://github.com/zayfod/pyozo.git
cd pyozo
pip install .
```

From source, for development:

```
git clone https://github.com/zayfod/pyozo.git
cd pyozo
pip install -r requirements.txt
pip install -e .
```


Support
-------

Bug reports and changes should be sent via GitHub:

[https://github.com/zayfod/pyozo](https://github.com/zayfod/pyozo)


Disclaimer
----------

This project is not affiliated with [Ozo EDU, Inc.](https://ozobot.com/)
