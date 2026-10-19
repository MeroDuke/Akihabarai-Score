from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_brand_policy_distinguishes_forks_without_restricting_gpl_rights():
    policy = (ROOT / "docs" / "policies" / "brand_policy.md").read_text(
        encoding="utf-8"
    )

    assert "does not modify the GNU GPL" in policy
    assert "modified and unofficial" in policy
    assert "No registered trade mark" in policy
    assert "commercial use" in policy
    assert "®" not in policy


def test_creator_credit_is_explicitly_voluntary():
    guideline = (
        ROOT / "docs" / "policies" / "creator_guidelines.md"
    ).read_text(encoding="utf-8")

    assert "önkéntes alkotói kérés, nem licencfeltétel" in guideline
    assert "voluntary creator request, not a license condition" in guideline
    assert "A pontozáshoz az Akihabarai Score alkalmazást használtuk" in guideline
    assert "Scoring was created with Akihabarai Score" in guideline


def test_release_workflows_keep_brand_and_creator_documents_out_of_portable_package():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "BRAND_POLICY.md" not in workflow
        assert "CREATOR_GUIDELINES.md" not in workflow
