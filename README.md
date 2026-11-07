# oscterm

Scott Lumsden, 2026

A command-line terminal for OSC communication, written in python.

Written primarily to make it easier to develop and debug OSC commands for [nymphes-osc](https://github.com/jtpack/nymphes-osc) and [Blue and Pink Synth Editor](https://github.com/jtpack/Blue-and-Pink-Synth-Editor).
However, it should be useful to anyone who needs to send and receive OSC messages from the terminal.

Platforms:
- macOS
- Windows (Untested)
- Linux, including Raspberry Pi OS (Untested)


# Installation

## Option A: Installing With pipx

### 1. Make sure git is installed.

### 2. Install pipx if it isn't already installed

macOS:
- Use Homebrew to install pipx: `brew install pipx`
- `pipx ensurepath`

Windows (using PowerShell):
- `py -m pip install --user pipx`
- `py -m pipx ensurepath`

Linux (Ubuntu or Raspberry Pi OS):
- `sudo apt update`
- `sudo apt install pipx`
- `pipx ensurepath`

### 3. install oscterm using pipx

macOS and Linux:
- Use pipx to install oscterm: `pipx install git+https://github.com/jtpack/oscterm.git`
- Later, to update oscterm when there's a new version: `pipx upgrade oscterm`

Windows:
- First clone the oscterm repository:
  - `cd ~`
  - `git clone https://github.com/jtpack/oscterm.git`
- Then install with pipx:
  - `cd oscterm`
  - `pipx install .`

## Option B: Download the Python Code and Run In a Virtual Environment

### 1. Clone This Repository

- From the terminal, navigate to a location where you'd like the files to live (we will assume your home folder): `cd ~`
- `git clone https://github.com/jtpack/oscterm.git`

### 2. Create a Virtual Environment for oscterm and Activate It

- Navigate to the oscterm directory: `cd ~/oscterm`

macOS and Linux:
- `python -m venv venv`
- `source venv/bin/activate`

Windows:
- `py -3 -m venv venv`
  - `venv\Scripts\activate`

_If you are using Windows PowerShell and get an error message indicating that running scripts is disabled on your system, enter the following command and then try again: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`_

### 3. Install The Required Python Packages and oscterm Itself Into the Virtual Environment
- `pip install -e .`

### 4. Run oscterm
- Make sure you are in the oscterm directory and the virtual environment is activated.
- Then simply type `oscterm`
