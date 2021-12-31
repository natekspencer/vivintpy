Prior to opening a PR request, it is encouraged to update the included Z-Wave device database by running the following command:

```python
python3 -m script.gen_zjs_device_config_db
```

Build and publish this package using:

```python
rm -rf dist
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload dist/*
```
