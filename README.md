# Simple Blockchain
This project is an attempt to implement a basic blockchain.

## Table of contents
* [General info](#general-info)
* [Screenshots](#screenshots)
* [Technologies](#technologies)
* [Setup](#setup)
* [Launch](#launch)
* [Status](#status)
* [Inspiration](#inspiration)
* [Contact](#contact)

## General info
This project is for training purpose, it is not aimed to implement something for production.
Further personnal improvements will be added in the future, all of them for training purpose.
I coded this blockchain to learn the technology and to solidify my knowledge in Python via online courses which this project is based on. 

## Screenshots

## Technologies
* HTML - version 5
* Python - version 3.8.5
* flask - version 1.1.2
* flask-cors - version 3.0.9
* pycryptodome - version 3.9.9

## Setup
This project has been only tested on Linux Manjaro Nibia 20.2.1.
### On Linux:
Install dependencies with pip3 (like flsak, flask-cors and pycryptodome):
```bash
pip3 install <name_of_dependency>
```
For Python and HTML, they should be installed on your Linux machine by default.

### On Windows:
No tests have been launched on Windows for the moment.

## Launch
After all dependencies has been installed, launch the project with a terminal on the source folder and type:
```bash
python node.py
```
It will launch a wallet with the default port 5000.
If you want to launch another waller with an adress of 5001, type:
```bash
python node.py -p 5001
```
You can launch as many wallet as you want on separate terminals.

## Status
This project is _in progress_ because documentation is missing, other functionnalities and polishing.

## Inspiration
Project based on tutorials of Maximilian from Academind

## Contact
Created by Flavien Chamay (thanks to Maximilian) [flavien.chamay@protonmail.com](https://protonmail.com)
