# oscterm

Scott Lumsden, 2026

A command-line terminal for OSC communication, written in python.

Written primarily to make it easier to develop and debug OSC commands for [nymphes-osc](https://github.com/jtpack/nymphes-osc) and [Blue and Pink Synth Editor](https://github.com/jtpack/Blue-and-Pink-Synth-Editor).

Currently in early development, so don't expect it to be fully functional yet...


# Installation

## 1. Clone This Repository

- From the terminal, navigate to a location where you'd like the files to live (we will assume your home folder): `cd ~`
- `git clone https://github.com/jtpack/oscterm.git`

## 2. Create a Virtual Environment for oscterm and Activate It

- Navigate to the oscterm directory: `cd ~/oscterm`

macOS and Linux:
- `python -m venv venv`
- `source venv/bin/activate`

Windows:
- `py -3 -m venv venv`
  - `venv\Scripts\activate`

_If you are using Windows PowerShell and get an error message indicating that running scripts is disabled on your system, enter the following command and then try again: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`_

## 3. Install The Required Python Packages and oscterm Itself Into the Virtual Environment
- `pip install -e .`

## 4. Run oscterm
- Make sure you are in the oscterm directory and the virtual environment is activated.
- Then simply type `oscterm`
