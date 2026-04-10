import unittest

from gitops_summary.prompts import (
    build_commit_retry_prompt,
    build_fallback_commit_message,
    build_fallback_commit_subject,
    build_prompt,
    clean_commit_response,
    coerce_commit_message,
    looks_like_commit_message,
    sanitize_commit_response,
)


class CommitPromptTests(unittest.TestCase):
    def test_build_prompt_requests_commit_subject_format(self) -> None:
        prompt = build_prompt("M  src/app.py", "diff --git a/src/app.py b/src/app.py")

        self.assertIn("First line: one concise git commit subject", prompt)
        self.assertIn("include a 1-3 sentence executive summary paragraph", prompt)
        self.assertIn("Do write a real commit message with subject line, summary paragraph", prompt)
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

    def test_build_fallback_commit_message_for_single_file(self) -> None:
        message = build_fallback_commit_message("## main\nM  src/gitops_summary/commit.py")

        self.assertEqual(
            message,
            "Update commit.py\n\n- Update src/gitops_summary/commit.py",
        )

    def test_build_fallback_commit_message_for_multiple_files(self) -> None:
        message = build_fallback_commit_message(
            "## main\nM  src/gitops_summary/commit.py\nM  src/gitops_summary/prompts.py",
        )

        self.assertEqual(
            message,
            "Update 2 files in src\n\n- Update src/gitops_summary/commit.py\n- Update src/gitops_summary/prompts.py",
        )

    def test_build_fallback_commit_subject_for_multiple_files(self) -> None:
        subject = build_fallback_commit_subject(
            "## main\nM  src/gitops_summary/commit.py\nM  src/gitops_summary/prompts.py",
        )

        self.assertEqual(subject, "Update 2 files in src")

    def test_build_fallback_commit_message_handles_rename(self) -> None:
        message = build_fallback_commit_message("## main\nR  old_name.py -> new_name.py")

        self.assertEqual(
            message,
            "Rename old_name.py to new_name.py\n\n- Rename old_name.py to new_name.py",
        )

    def test_sanitize_commit_response_strips_planning_language_but_keeps_commit(self) -> None:
        response = """Based on the implementation plan and source files, here are my observations:
Update search ingestion flow

Backend:
- Add upload validation for PDF and DOCX files
- Tighten chunk persistence in storage.py

Let me know if you need any specific areas investigated further!
"""

        sanitized = sanitize_commit_response(response)

        self.assertEqual(
            sanitized,
            "Update search ingestion flow\n\n- Add upload validation for PDF and DOCX files\n- Tighten chunk persistence in storage.py",
        )

    def test_looks_like_commit_message_accepts_sanitized_commit_with_phase_language_removed(self) -> None:
        response = """Based on the implementation plan and source files, here are my observations on alignment with Phase 1:
Improve document sync flow

- Add retry handling in sync worker
- Update API validation for ingest requests
"""

        self.assertTrue(looks_like_commit_message(response))

    def test_looks_like_commit_message_allows_phase_in_real_commit_subject(self) -> None:
        response = """Implement Phase 1 MVP with local ingestion and in-memory search

This commit delivers the initial MVP implementation.

- Define Pydantic models for request and response schemas
"""

        self.assertTrue(looks_like_commit_message(response))

    def test_coerce_commit_message_preserves_summary_and_bullets(self) -> None:
        response = """Based on the implementation plan and source files, here are my observations:
Improve document sync flow

This change tightens ingestion validation and cleans up sync behavior.

Backend:
- Add retry handling in sync worker
- Update API validation for ingest requests
"""

        message = coerce_commit_message(
            response,
            "## main\nM  backend/app/services.py\nM  backend/app/main.py",
        )

        self.assertEqual(
            message,
            "Improve document sync flow\n\nThis change tightens ingestion validation and cleans up sync behavior.\n\n- Add retry handling in sync worker\n- Update API validation for ingest requests",
        )

    def test_coerce_commit_message_uses_fallback_subject_when_no_subject_present(self) -> None:
        response = """Backend:
Improves validation around uploads and sync retries.

- Add retry handling in sync worker
- Update API validation for ingest requests
"""

        message = coerce_commit_message(
            response,
            "## main\nM  backend/app/services.py\nM  backend/app/main.py",
        )

        self.assertEqual(
            message,
            "Update 2 files in backend\n\nImproves validation around uploads and sync retries.\n\n- Add retry handling in sync worker\n- Update API validation for ingest requests",
        )

    def test_sanitize_commit_response_drops_next_steps_section(self) -> None:
        response = """Implement Phase 1 MVP with local ingestion and in-memory search

This commit delivers the initial MVP implementation.

- Define Pydantic models for request and response schemas

Next steps:
- Integrate OpenSearch
- Wire up Bedrock
"""

        sanitized = sanitize_commit_response(response)

        self.assertEqual(
            sanitized,
            "Implement Phase 1 MVP with local ingestion and in-memory search\n\nThis commit delivers the initial MVP implementation.\n\n- Define Pydantic models for request and response schemas",
        )


if __name__ == "__main__":
    unittest.main()