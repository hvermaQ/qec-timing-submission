# Environment

The first build uses Python 3.9+ standard library, the repository's dependency-free
surface-code definition, and clang for LLVM assembly. It does not need a Guppy
recompile. Exact tool versions are saved alongside every generated program.

The full H2 environment is not installed in this checkout. For future fresh
Guppy compilation and aqora access, the repository's existing reference pins are
`envs/h2.txt` (Python 3.11). Install any new virtual environment under
`SG_final_round/env/.venv-h2/` and keep its installation logs here. Those Linux
reference pins have not been verified on this macOS host.

No dependency downloads are needed for the current local artifact test.
