# Implementation notes

The implementation uses the frozen case order and four rules. It uses only the Python standard library.

Each connection sets a private cache, read_uncommitted=0, synchronous=FULL, foreign_keys=ON, and a five-second busy timeout. Readers, source writes, gate writes, and audit reads use explicit BEGIN IMMEDIATE transactions. The schema contains the five required tables. The gate has one row. An action row refers to its saved decision.

A worker process runs a new copy of study.py. The first attempt uses os._exit(73) at the declared boundary. Its last phase record is flushed to stdout first. Recovery uses a new process and a fresh connection. No worker cleanup handler replaces the process exit. The driver records the actual process exit status, stdout, stderr, PID, elapsed time, and local CPU use.

The audit before forced gate opening is retained in audit. The audit after the forced opening is retained in post_intervention_audit. The driver does not supply either audit to the reader. A reader with a closed gate records a refusal in the trace and reads no source fields.

The final table snapshot is saved before probes and after probes. Every database has an integrity check and a WAL checkpoint. The logical dump retains all SQL table data. Physical database files remain in the requested private database directory and in the compressed archive. PID and timing logs are separate from deterministic logical data. The archive contains physical database evidence, not a deterministic logical output contract.

The serial boundary controls use one ordinary whole-transaction worker process. Its exit status is recovery_status. They have no interrupted first attempt, so expected_exit_status and exit_status are null. The known cut check remains separate from membership in the allowed serial set.

The script refuses to use existing output or database directories. It saves code, schema, plan, and configuration hashes before the first control or scored trial. It reports progress after every 128 scored trials. It retains an unknown trial and stops on a process, SQL, integrity, logging, or resource failure. Fully observed adverse decisions remain valid results.

No planned rule, case, or oracle was changed during implementation.
