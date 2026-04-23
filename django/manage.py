#!/usr/bin/env python3
# Entrypoint de comandos Django.
import os
import sys


def main():
    # Define modulo de configuracao padrao.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoluipc_backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django nao encontrado no ambiente atual.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
