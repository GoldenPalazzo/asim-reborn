# ASIM reborn

Proof of concept

This is a IDE for the Motorola 68000 CPU. It features an editor, a compiler
and a debugger.

I made this because my university classes are using an obsolete tool (known
as ASIM, Ambiente di SIMulazione, literally "simulation environment") which was
developed by Italian computer scientist/engineer Antonino Mazzeo.

With the utmost respect for prof. Mazzeo, ASIM was developed in 1996, and now in
2024 not everyone uses the same IBM laptop with Windows 95.

So, using `vasm` as compiler and `bare68k` as python wrapper to the `Musashi`
M68K emulator, I decided to build a bit more modern IDE to be used for these
classes. But most importantly, I decided to build an IDE that is able to run
on modern computers, and also on Linux and Mac OS X.

Providing also the sources, I hope this repo will be used and forked in the
future to keep it up to date.

## Installation

Currently I'm teaching myself how to automate build processes through
Github Actions, so probably the latest non-failed build might work right now.

When I'll polish it a bit more, I will post a stable releases in the proper tab.

If you wish to build it yourself, here are the instructions

1. Download Python 3.12 following the favorite method of your OS.
2. Clone the repo by clicking the green button or by running
   ```
   $ git clone https://github.com/GoldenPalazzo/asim-reborn.git
   ```
3. Get in the newly cloned repo
  
  - I strongly advise you to create a virtual environment via
    ```
    $ python -m venv .venv
    ```
    and then
    
    - Linux
    ```
    $ source .venv/bin/activate
    ```
    - Windows
    ```
    > .\.venv\Scripts\Activate.ps1
    ```
5. Download external resources
    - Linux
    ```
    $ ./src/prepare_repo.sh
    ```
    - Windows
    ```
    > .\src\prepare_repo.bat
    ```
4. Install dependencies
   ```
   $ pip install -r requirements.txt
   $ pip install lib/bare68k-0.1.2-cp312-cp312-osname_arch.whl
   ```
   changing `osname` and `arch` accordingly with the previously downloaded file.
6. Run.
   ```
   $ python src/main.py
   ```

## Usage

Write whatever program you want. Compile it and then run.

## Current limitations

At this moment:
- Fonts don't render correctly in Windows
- Mac OS build coming soon because I have to figure out how to automate the build
  of vasm
- There is no way to see the RAM memory. Only the registers
