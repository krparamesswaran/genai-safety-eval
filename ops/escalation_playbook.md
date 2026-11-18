# Escalation Playbook and Feedback Loop

## When a case escalates
A case escalates when (a) the classifier marks `needs_review: true`, (b) a user appeals a decision, or (c) a missed violation is reported after the fact.

## Investigation steps (for every escalated miss)
1. **What happened:** record the message, the classifier output and the human label.
2. **Why it happened:** tag the root cause:
   - `policy_gap`: the policy does not describe this pattern
   - `ambiguous_policy`: the policy covers it but the wording is unclear
   - `context_needed`: the decision needs context the classifier did not have
   - `model_error`: the policy is clear and the model still got it wrong
   - `label_noise`: the human label itself looks wrong
3. **Prevent recurrence:** pick the fix that matches the root cause:
   - `policy_gap` or `ambiguous_policy` → update `policy/content_policy.md` (new version)
   - `context_needed` → route this pattern to human review by default
   - `model_error` → add a worked example to the prompt, or a stricter rule
   - `label_noise` → log it and exclude it from scoring

## Feedback loop
1. Review all false negatives from `results/false_negatives_v1.csv` and tag each root cause.
2. Write policy v2 addressing the top 2 root causes.
3. Re-run `classify.py --policy-version v2` and `evaluate.py --policy-version v2` on the same sample.
4. Compare v1 vs v2 recall and precision. Keep v2 only if missed violations drop without a large rise in false positives.

## Priorities
Missed violations (false negatives) are treated as more serious than over-flagging, because a miss leaves harmful content up. Threats are reviewed first.
