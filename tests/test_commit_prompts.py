import unittest

from gitops_summary.prompts import (
    build_commit_retry_prompt,
    build_prompt,
    clean_commit_response,
    looks_like_commit_message,
)


class CommitPromptTests(unittest.TestCase):
    def test_build_prompt_requests_commit_subject_format(self) -> None:
        prompt = build_prompt("M  src/app.py", "diff --git a/src/app.py b/src/app.py")

        self.assertIn("First line: one concise git commit subject", prompt)
        self.assertIn("Do NOT write an executive summary", prompt)
        self.assertIn("Start directly with the commit subject line", prompt)

    def test_build_commit_retry_prompt_mentions_invalid_answer(self) -> None:
        retry_prompt = build_commit_retry_prompt(
            "M  src/app.py",
            "diff --git a/src/app.py b/src/app.py",
            invalid_response="Based on the implementation plan, here are my observations...",
        )

        self.assertIn("The previous answer was invalid", retry_prompt)
        self.assertIn("Invalid answer:", retry_prompt)
        self.assertIn("Based on the implementation plan", retry_prompt)

    def test_clean_commit_response_removes_preamble_and_trailing_chatter(self) -> None:
        response = """Here is the commit message:

**Add retry guard for commit generation**

- Retry Bedrock when output looks like a review
Let me know if you need anything else!
"""

        cleaned = clean_commit_response(response)

        self.assertEqual(
            cleaned,
            "Add retry guard for commit generation\n\n- Retry Bedrock when output looks like a review",
        )

    def test_looks_like_commit_message_rejects_review_style_output(self) -> None:
        review_output = """Based on the implementation plan and source files, here are my observations on alignment with Phase 1:

Backend:
- Added API endpoints
"""

        self.assertFalse(looks_like_commit_message(review_output))

    def test_looks_like_commit_message_accepts_normal_commit_message(self) -> None:
        commit_message = """Tighten commit generation prompt

- Add system prompt for commit-only responses
- Retry when the model returns review-style output
"""

        self.assertTrue(looks_like_commit_message(commit_message))


if __name__ == "__main__":
    unittest.main()