"""Explicit QIR `sleep` between X-memory extraction rounds (H2-1E / H2-2E emulators, H2-1 / H2-2).

Merged from `SG_final_round/` (see MIGRATION.md). Layout:

    paths      every path, `resolve_recorded` for paths stored in historical JSON, write helpers
    qir        shared QIR text helpers and the optional clang assembly checks
    builders/  the QIR program builders (folder names reproduce the committed build folders)
    mapping    the skip-index-5 qubit mapping for physical H2-2 d=5
    decoder    the approved physical H2-2 decoder policies (see /AGENTS.md)
    jobs       provider options and the aqora check/submit/fetch/status code (aqora is
               imported only inside functions; every call that contacts aqora needs confirm=True)

Importing this package never imports aqora and never writes a file.
"""
