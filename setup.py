from setuptools import setup, find_packages

setup(
    name="tangods_pilctriggergategenerator",
    version="0.0.1",
    description="High level device server in order to interact with PiLC TangoDS running firmware SXR_Delay_Gate_21_05_06",
    author="Daniel Schick",
    author_email="dschick@mbi-berlin.de",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "PiLCTriggerGateGenerator = tangods_pilctriggergategenerator:main"
        ]
    },
    license="MIT",
    packages=["tangods_pilctriggergategenerator"],
    install_requires=[
        "pytango",
    ],
    url="https://github.com/MBI-Div-b/pytango-PiLCTriggerGateGenerator",
    keywords=[
        "tango device",
        "tango",
        "pytango",
    ],
)
