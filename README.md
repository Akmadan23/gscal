# gscal (GTK Simple Calendar)
Extremely minimal calendar app inspired by [Gsimplecal](https://github.com/dmedvinsky/gsimplecal).

## Install
Releases are available over on [PyPI](https://pypi.org/project/gscal/) and can be installed via pip:

```
pip install gscal
```

On Arch Linux gscal is available in the AUR:

```
[paru/yay] -S gscal
```

## Configuration
Gscal looks for a configuration file at `~/.config/gscal/gscal.toml` if not specified by the user with the `-c` flag.
If no config file was it uses the [default configuration](https://github.com/Akmadan23/gscal/blob/master/config/gscal.toml).
> Currently only 3 options are available, more to come in the future.
