from setuptools import setup, find_packages

setup(
    name="synth8",
    version="0.1.0",
    author="Valerio Poggi",
    description="Modular synthesizer engine for real-time audio in Python",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "sounddevice",
        "scipy",
        "pynput"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8"
)

