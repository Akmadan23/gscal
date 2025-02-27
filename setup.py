import setuptools as st

st.setup(
    name = "gscal",
    version = "0.3.1",
    license = "GPL-3",
    license_files = ["LICENSE"],
    author = "Azad Ahmadi",
    author_email = "azadahmadi@mailo.com",
    description = "GTK Simple Calendar",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
    url = "https://github,com/Akmadan23/gscal",
    packages = st.find_packages(where = "src"),
    package_dir = { "": "src" },
    package_data = { "gscal": ["data/*"] },

    python_requires = ">=3.6",

    install_requires = [
        "PyGObject",
        "toml"
    ],

    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],

    entry_points = {
        "console_scripts": ["gscal = gscal.__main__:run"]
    }
)
