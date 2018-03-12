## Raven version in InaSAFE
* 6.6.0 (2018-02-12)
* https://github.com/getsentry/raven-python/releases

QGIS is provided with a old version of contextlib. I had to manually update the
Raven package. If you update Raven, you might need to check this change.

In `raven/base.py`, replace:
```python
if sys.version_info >= (3, 2):
    import contextlib
else:
    import contextlib2 as contextlib
```
by:

```python
try:
    import contextlib
except ImportError:
    import contextlib2 as contextlib
```

I could remove 'raven/contrib' folder to make the library smaller.