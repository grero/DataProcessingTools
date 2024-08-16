from distutils.core import setup

setup(name="DataProcessingTools",
      version="0.23.0",
      description="""Tools for processing data with hierarchical organization""",
      url="https://github.com/grero/DataProcessingTools.git",
      author="Roger Herikstad",
      author_email="roger.herikstad@gmail.com",
      license="MIT",
      packages=["DataProcessingTools"],
      package_data={"DataProcessingTools": ["config.json"]},
      install_requires=["numpy",
                        "scipy",
                        "matplotlib",
                        "h5py",
                        "hickle",
                        "pathlib"]

      )
