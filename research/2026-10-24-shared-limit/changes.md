# Plan and analysis record

Date: 2026-10-24.

The source search and design review preceded the final experiment plan. The earlier candidate with a separate last read was not selected or run.

The first plan was saved at 14:21:11.966725 UTC. Before implementation, a separate reviewer found an overbroad metadata invariance check. A SharedEpoch refusal can indirectly change another worker's capacity and decision. The corrected check applies only to pairs with no SharedEpoch worker. The corrected plan was saved at 14:22:04.140375 UTC. Both plans and both freeze records remain available. No experimental results drove this correction.

The main code was then written and run twice. No main-run code correction or third full run was needed. Both complete runs passed. The expected SQLITE_BUSY_SNAPSHOT control error was a passed control, not an unexpected failure.

After execution, summarize_pairs.py extracted the planned paired metadata comparisons and one adverse example for each failing policy pair. It did not add cases or change outcomes. These derived files matched across both saved runs. The report's short algebraic count derivations were checked against the independent evaluator and SQL evidence.

The separate pure evaluator was frozen before main-code or result access. The SQL comparison adapter was frozen after evidence-schema inspection and before its full comparison. The reviewer read the main runner only after the comparison passed. The artifact preserves these distinct review boundaries.
