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
    @echo "creating venvs"
    hatch env create
    hatch env show

create_reqs:
    @echo "creating requirements files"
    hatch dep show requirements --project-only > requirements.txt
    hatch dep show requirements --env-only > requirements_dev.txt

create_pipreqs:
    @echo "creating requirements (pipreqs)"
    pipreqs --force --savepath requirements.txt src/

install_deps:
    @echo "installing dependencies locally"
    hatch dep show requirements --project-only > requirements.tmp
    pip install -r requirements.tmp

install_deps_dev:
    @echo "installing dev dependencies locally"
    hatch dep show requirements --env-only > requirements_dev.tmp
    pip install -r requirements_dev.tmp

test_shfmt:
    @echo "testing with shfmt"
    find . -type f \( -name "**.sh" -and -not -path "./.**" -and -not -path "./venv**" \) -exec shfmt -d -i 4 -bn -ci -sr "{}" \+;

format_shfmt:
    @echo "formatting with shfmt"
    find . -type f \( -name "**.sh" -and -not -path "./.**" -and -not -path "./venv**" \) -exec shfmt -w -i 4 -bn -ci -sr "{}" \+;

lint *args:
    @echo "linting project"
    just show_system_info
    just test_shfmt
    hatch run lint:all {{ args }}

format *args:
    @echo "formatting project"
    just show_system_info
    just format_shfmt
    hatch run lint:fmt {{ args }}

check *args:
    just format {{ args }}
    just lint {{ args }}

test *args:
    @echo "running tests"
    just show_system_info
    hatch run test:test {{ args }}

coverage *args:
    @echo "running tests with coverage report"
    just show_system_info
    hatch run test:cov {{ args }}

build *args:
    @echo "building project"
    just show_system_info
    hatch build --clean {{ args }}

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
    just get-docs {{ args }}
    just build-docs {{ args }}
