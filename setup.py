from setuptools import setup

setup(
    name="timerpal",
    version="0.0.1",
    description="Simple terminal timer with curses",
    author="Simon Robles",
    author_email="simon.g.robles@gmail.com",
    license="GPLv3",
    url="https://github.com/Simon-CPSC/TimerPal",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Topic :: Utilities"
    ],
    install_requires=[
        "click >= 2.0",
        "pyfiglet >= 0.7",
        "python-dateutil",
        "playsound",
        "gobject",
        "PyGObject"
    ],
    py_modules=["timerpal"],
    entry_points={
        'console_scripts': [
                "timerpal=timerpal:main"
            ],
        },
)
