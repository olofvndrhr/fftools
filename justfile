#!/usr/bin/env just --justfile

default: show_receipts

set shell := ["bash", "-uc"]
set dotenv-load := true

show_receipts:
    just --list

show_system_info:
    @echo "=================================="
    @echo "os : {{ os() }}"
    @echo "arch: {{ arch() }}"
    @echo "justfile dir: {{ justfile_directory() }}"
    @echo "invocation dir: {{ invocation_directory() }}"
    @echo "running dir: `pwd -P`"
    @echo "=================================="

setup:
    asdf install

create_venv:
    @echo "creating venv"
    hatch env create
    hatch env show

install_deps:
    @echo "installing dependencies"
    python3 -m hatch dep show requirements --project-only > requirements.tmp
    pip3 install -r requirements.tmp

install_deps_dev:
    @echo "installing dev dependencies"
    python3 -m hatch dep show requirements --env-only > requirements_dev.tmp
    pip3 install -r requirements_dev.tmp

create_reqs:
    @echo "creating requirements"
    pipreqs --force --savepath requirements.txt src/

test_shfmt:
    @echo "testing with shfmt"
    find . -type f \( -name "**.sh" -and -not -path "./.**" -and -not -path "./venv**" \) -exec shfmt -d -i 4 -bn -ci -sr "{}" \+;

format_shfmt:
    @echo "formatting with shfmt"
    find . -type f \( -name "**.sh" -and -not -path "./.**" -and -not -path "./venv**" \) -exec shfmt -w -i 4 -bn -ci -sr "{}" \+;

lint:
    @echo "linting project"
    just show_system_info
    just test_shfmt
    hatch run lint:all

format:
    @echo "formatting project"
    just show_system_info
    just format_shfmt
    hatch run lint:fmt

test:
    @echo "running tests"
    just show_system_info
    hatch run test:test

coverage:
    @echo "running tests with coverage report"
    just show_system_info
    hatch run test:cov

build:
    @echo "building project"
    just show_system_info
    hatch build --clean

get-docs *args:
    @echo "getting docs"
    just show_system_info
    bash docs/get_docs.sh

build-docs *args:
    @echo "building docs"
    just show_system_info
    hatch run docs:build {{ args }}

make-docs *args:
    @echo "making docs"
    just get-docs
    just build-docs
