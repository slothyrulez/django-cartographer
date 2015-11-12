# django-cartographer
Agnostic manifest registry assets manager for django

Based on [owais](https://github.com/owais) [django-webpack-loader](https://github.com/owais/django-webpack-loader) and [sveetch]( https://github.com/sveetch) [recalbox-manager](https://github.com/sveetch/recalbox-manager)


Features:
- Common registry holding parsed assets structures
- Load assets from [webpack-bundle-tracker](https://github.com/owais/webpack-bundle-tracker)
- Load assets from a json file

Quick start
-----------
Install django-cartographer
```
pip install django-cartographer
```

Add "cartographer" to INSTALLED_APPS
```
...
"cartographer",
...
```

Configuration
-------------

### Assets from webpack-bundle-tracker
### Assets from file


Example
-------

On the example directory there is a minimal application
