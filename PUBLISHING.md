# Pending source publication procedure

Target owner `KaiserIIII`, repository `migrationwitness`, public source experimental edition. **NOT EXECUTED.** This file is a handoff, not authorization. Do not create a remote, push or run hosted workflows until the owner explicitly authorizes publication of the frozen candidate.

1. Read PUBLICATION_READINESS.md and external final DELIVERY.json; compare `git rev-parse HEAD`, Git tree, clean worktree and PUBLIC_FILES.json inventory with its exact frozen candidate/ZIP hashes. Verify the Git Bundle and restore it if needed. Never substitute an unreviewed working tree or old candidate.
2. Confirm `gh api user --jq .login` is KaiserIIII and every author/committer in the candidate history has the verified `104786001+KaiserIIII@users.noreply.github.com` identity. Do not request/store a token or rewrite another contributor.
3. Audit the exact tracked history/public paths, excluding evidence/runtimes/caches. Check whether the target repository already exists before any create; do not overwrite unrelated remote history.
4. After authorization, create the public repository without an automatic README/license/Release. A reviewed command is `gh repo create KaiserIIII/migrationwitness --public --description "Disposable PostgreSQL migration contract experiments and runtime evidence"`. Add its HTTPS remote to the verified source clone, then push only the frozen candidate `HEAD:main`. Do not push all branches/tags or private backup refs; no force push.
5. Compare remote main SHA/tree/path inventory against the frozen commit with read-only GitHub API/git commands. Confirm public README/中文说明/install/examples/license and derived summary. If there is a mismatch, stop the publication workflow and preserve recovery notes.
6. Observe the configured Windows/Linux16/Linux17 Actions for that exact SHA. Hosted CI is currently NOT RUN. Fix only real reproduced release/platform issues with regression evidence; rerun the affected checks, and update SHA/inventory audit transparently. Do not lower assertions or call static syntax checks hosted success.
7. Report final URL, exact SHA, Git tree, public path count and hosted job results. Keep limits visible. Do not publish PyPI, an installer, official Release, service or paper. Freeze afterward.

If GitHub authorization, repository ownership or publication scope is ambiguous/unavailable, stop remote operations and retain these recovery steps; never ask for passwords or tokens.
