# Security policy

Use GitHub private security advisories to report vulnerabilities. Do not publish secrets or exploit details in an issue.

The CLI makes no network requests and requires no credentials. It reads a local JSON portfolio and writes to a selected directory. Run untrusted inputs with least privilege, review output paths, and avoid embedding confidential portfolio data in artifacts intended for sharing.

Report publication does not follow application-controlled output-directory symlinks or pre-existing report symlinks. Every artifact is staged before commit, and a commit failure restores the complete previous set or leaves a previously empty destination empty. Cooperating writers serialize publication with an exclusive advisory lock on the verified output directory; unsupported or failed locking fails closed. The lock protects only cooperating processes on filesystems that honor `flock`-style advisory locks, so it does not serialize unrelated writers or filesystems that ignore those locks. Target identities are rechecked immediately before publication, and ambiguous rename outcomes are reconciled before rollback. Descriptor-relative and compatibility-fallback publication both close acquired temporary descriptors if text-stream setup fails. Invalid output paths produce CLI status `2`. User-selected input paths are read as ordinary local files, so an explicitly supplied input symlink is followed; apply normal filesystem trust and permission controls to portfolio inputs.

Only the latest release is supported.
