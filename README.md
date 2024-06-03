<p align="center">
    <img width="512" src="https://raw.githubusercontent.com/GoldenPalazzo/asim-reborn/main/logo.png"></img>
</p>

<h1 align="center">
    ASIM Reborn - Simple multiplatform 68k IDE
</h1>

This is a IDE for the Motorola 68000 CPU. It features an editor, a compiler
and a debugger.

I made this because my university classes are using an obsolete tool (known
as ASIM, Ambiente di SIMulazione, literally "simulation environment") which was
developed by Italian computer scientist/engineer Antonino Mazzeo.

The software was originally developed for Windows 95 and never had an update
past 1996. The making of this project was out of sheer necessity to have a
working IDE to follow the lessons that worked on Linux.
Since I'm making it in Python, I thought to build it for Windows and OS X as
well with `PyInstaller`.

Using `bare68k` python library forked by me for Python 3.12 and wrapping the
`vasm` compiler, this project now reached a usable state, with the full list
of features below.

I hope this project gets picked up by someone since I'm very very very prone to
get bored easily when a project is half completed.

## Table of contents

1. [Installation](#install)
2. [Building](#build)
3. [Usage](#usage)
4. [Features](#features)
5. [Collaboration and issues](#collab)

<a id="install"></a>
## Installation

Check out the [releases](https://github.com/GoldenPalazzo/asim-reborn/releases)
tab and follow the instructions to install the latest version.

If you are a masochist or actually need to build it yourself for your needs,
follow the instructions below.

<a id="build"></a>
## Building

Although it's preferable to download the precompiled binary from the releases
tab, if you ever need to build it yourself, here are the instructions.

1. Download Python 3.12
2. Clone the repo by clicking the green button or by running

   ```bash
   git clone https://github.com/GoldenPalazzo/asim-reborn.git
   ```

3. Get in the newly cloned repo

  - I strongly advise you to create a virtual environment via

    ```bash
    python -m venv .venv
    ```

    - Linux

    ```bash
    source .venv/bin/activate
    ```

    - Windows

    ```bat
    .\.venv\Scripts\Activate.ps1
    ```

### Linux / Mac OS

4. Download external resources

    ```bash
    ./src/prepare_repo.sh
    ```

    (make sure you have installed `brew` on OS X, and installed GNU coreutils
    via `$ brew install coreutils`)
5. Build vasm

    ```bash
    ./src/build_vasm.sh
    ```

6. Build bare68k

    ```bash
    ./src/build_bare68k.sh
    ```

7. (MAKE SURE YOU'RE IN THE VIRTUALENVIRONMENT) Install pip dependencies

    ```bash
    python -m pip install pip pyinstaller
    pip install -r requirements.txt
    pip install lib/bare68k*.whl
    ```

8. Build.

    ```bash
    ./src/build.sh
    ```

### Windows

4. Download external resources

    ```bat
    .\src\prepare_repo.bat
    ```

5. (MAKE SURE YOU'RE IN THE VIRTUALENVIRONMENT) Install pip dependencies

    ```bat
    set PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
    python -m pip install pip pyinstaller
    pip install -r requirements.txt
    pip install .\lib\bare68k-0.1.2-cp312-cp312-win_amd64.whl
    ```

6. Build.

    ```bat
    .\src\build.bat
    ```

The entire folder `AsimReborn` inside `dist` will be the final product of our
build. Feel free to modify the build scripts to best suit the artifact to your
needs (e.g. creating a single file instead of a single directory).

### Using it via python

You can also not build any executable and just run it via python with

```bash
python src/main.py
```

<a id="usage"></a>
## Usage

Write code as usual and then save your program via the menu or by clicking
`<Ctrl-S>`. After saving, you can compile your program in the same directory
it is present by clicking `<F5>`, running with `<F6>`, stepping with `<F7>`
and stopping with `<F8>`.

There are two docks: compilation and execution dock.

- The compilation dock literally shows the output of the `vasm` assembler. Soon
I will let the user manually choose the compilation flags. For now, they should
work good for generally every user.
- The execution dock features
  - a memory viewer that shows 32 longword addresses in hex and lets you pick the
  desired address to see.
  - a variable watching panel: insert the address and choose the representation
  you'd like to see for debug purposes between
    - Unsigned/Signed/Hexadecimal byte int
    - Unsigned/Signed/Hexadecimal word int
    - Unsigned/Signed/Hexadecimal longword int
    - Single ASCII character
    - Null termined ASCII string
  - all M68k registers in hexadecimal and formatted status register.
  - step and stop buttons.

<a id="features"></a>
## Features

- [x] Creating, opening, saving scripts.
- [x] Compilation and execution of M68K assembly in Motorola syntax.
- [x] Step by step execution.
- [ ] Fast run execution.
- [ ] Breakpoints.
- [x] Watching variables under different formats.
- [x] Memory viewer and stack pointer pointer.
- [x] Registries and formatted status register.
- [x] Status register info dialogue.
- [x] Compatible with ASIM written programs.
- [x] Syntax highlighting using Monokai color scheme.
- [ ] Customizable color scheme via settings.
- [ ] Settings menu.
- [x] Error highlighting at compile time.

<a id="collab"></a>
## Collaboration and issues

I'm open to all kind of pull requests at the moment, and also any kind of
bug report in the issues tab.

