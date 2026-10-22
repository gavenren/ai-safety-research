# Failures and changes

Both model runs completed with no execution or semantic-check failure. No case was excluded or replaced. There are zero unknown cases. All six deterministic files matched in the clean repeat.

A document-write command used package-relative paths while its working directory was already the package. Seven file writes therefore failed with “no such file or directory.” That command also ran the second model run successfully. The next comparison command failed because compare.py had not been created. The files were then saved from the correct directory and comparison passed. No third model run occurred. These were packaging and command-path errors, not adverse model outcomes.

Source access failures are listed in source_search.md. Before implementation, a timing error was found in that record: the draft said the last checklist sections had been read before they were opened. source_supplement.md corrects the timing. Those sections were then read before code and execution. Frozen inputs and hashes were preserved. No question, hypothesis, method, case, or measure changed.

The program records a normalized command with study.py. invocations.txt records the exact run commands. Source and output hashes identify the executed code.
