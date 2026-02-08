#!/usr/bin/env just --justfile

default: show-receipts

set shell := ["bash", "-uc"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set dotenv-load := true

show-receipts:
    just show-system-info
    just --list

show-system-info:
    @echo "=================================="
    @echo "os : {{ os() }}"
    @echo "arch: {{ arch() }}"
    @echo "justfile dir: {{ justfile_directory() }}"
    @echo "invocation dir: {{ invocation_directory() }}"
    @echo "running dir: `pwd -P`"
    @echo "=================================="

setup:
    asdf install

create-venv:
    @echo "creating venvs"
    hatch env create
    hatch env show

create-reqs:
    @echo "creating requirements files"
    hatch dep show requirements --project-only > requirements.txt
    hatch dep show requirements --env-only > requirements-dev.txt

create-pipreqs:
    @echo "creating requirements (pipreqs)"
    pipreqs --force --savepath requirements.txt src/

install-deps:
    @echo "installing dependencies locally"
    hatch dep show requirements --project-only > requirements.tmp
    pip install -r requirements.tmp

install-deps-dev:
    @echo "installing dev dependencies locally"
    hatch dep show requirements --env-only > requirements-dev.tmp
    pip install -r requirements-dev.tmp

lint *args:
    @echo "linting project"
    shfmt -d -i 4 -bn -ci -sr .
    hatch run lint:all {{ args }}

format *args:
    @echo "formatting project"
    shfmt -w -i 4 -bn -ci -sr .
    hatch run lint:fmt {{ args }}

check:
    just format
    just lint

test *args:
    @echo "running tests"
    hatch run test:test {{ args }}

coverage *args:
    @echo "running tests with coverage report"
    hatch run test:cov {{ args }}

build *args:
    @echo "building project"
    hatch build --clean {{ args }}

get-docs:
    @echo "getting docs"
    bash docs/get_docs.sh

build-docs *args:
    @echo "building docs"
    just show_system_info
    hatch run docs:build {{ args }}

make-docs *args:
    @echo "making docs"
    just get-docs {{ args }}
    just build-docs {{ args }}
