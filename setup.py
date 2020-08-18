from setuptools import setup

setup(name="DataProcessingTools",
      version="0.15.0",
      description="""Tools for processing data with hierarchical organization""",
      url="https://github.com/grero/DataProcessingTools.git",
      author="Roger Herikstad",
      author_email="roger.herikstad@gmail.com",
      license="MIT",
      packages=["DataProcessingTools"],
      include_package_data=True,
      package_data = {"": ["config.json"]},
      )
