# Count from one to ten

[← Back to top-level README](../../../../README.md)

Create a bounded semantic workflow that counts from 1 through 10 inclusive and returns the ordered values.

Initialize a workflow-scoped AtomSpace memory cell named `current_count` to 1 and an ordered `collected_values` cell to an empty list. For each iteration, read `current_count`, append that number to `collected_values`, and retain evidence linking the produced number to its iteration.

While `current_count` is less than 10, increment it by one and repeat the capture step. The loop must have an explicit maximum of 10 iterations and must never produce 11.

Return `count_values` equal to `[1,2,3,4,5,6,7,8,9,10]`, `final_count` equal to 10, and enough loop evidence to verify every iteration.
