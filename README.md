# ASIM reborn

Proof of concept

## Installazione venv

Ho avuto un casino di problemi, perché bare68k usa il python 3.6.15 come ultima
versione.

Dunque ho installato `pyenv` con

`pacman -S pyenv`

E aggiunto [pyvirtualenv](https://github.com/pyenv/pyenv-virtualenv)

In ogni caso ho avuto problemi perché non mi attivava il venv con la zsh,
quindi ho seguito [questa guida](https://github.com/pyenv/pyenv-virtualenv/issues/387#issuecomment-847855719).

E vabbè, mo mi devo mettere solo a faticare.

## Ambiente

Usando docker sono riuscito a preparare un ambiente (chiamato `68k-env`)
dove poter compilare e deassemblare tutti i programmi tranquillamente.

Basta cambiare le `ENV` all'interno di `Dockerfile` per poter avere l'ownership
corretta sui file generati.
