.PHONY: bump-major bump-minor bump-patch version-ai help

CURRENT_VERSION := $(shell head -1 VERSION)
MAJOR := $(word 1,$(subst ., ,$(CURRENT_VERSION)))
MINOR := $(word 2,$(subst ., ,$(CURRENT_VERSION)))
PATCH := $(word 3,$(subst ., ,$(CURRENT_VERSION)))

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

bump-major: ## Bump major version (e.g. 2.0.0 -> 3.0.0)
	$(eval NEW_VERSION := $(shell echo $$(( $(MAJOR) + 1 )).0.0))
	@$(MAKE) _apply_version NEW_VERSION=$(NEW_VERSION)

bump-minor: ## Bump minor version (e.g. 2.0.0 -> 2.1.0)
	$(eval NEW_VERSION := $(MAJOR).$(shell echo $$(( $(MINOR) + 1 ))).0)
	@$(MAKE) _apply_version NEW_VERSION=$(NEW_VERSION)

bump-patch: ## Bump patch version (e.g. 2.0.0 -> 2.0.1)
	$(eval NEW_VERSION := $(MAJOR).$(MINOR).$(shell echo $$(( $(PATCH) + 1 ))))
	@$(MAKE) _apply_version NEW_VERSION=$(NEW_VERSION)

_apply_version:
	@echo "Bumping version: $(CURRENT_VERSION) -> $(NEW_VERSION)"
	@sed -i '1s/.*/$(NEW_VERSION)/' VERSION
	@sed -i 's/__version__ = ".*"/__version__ = "$(NEW_VERSION)"/' src/gitops_summary/_version.py
	@echo "Updated VERSION and _version.py to $(NEW_VERSION)"
	@echo "Don't forget to add a changelog entry in VERSION."

version-ai: ## Analyze new commits and update VERSION changelog via Bedrock
	@python -c "\
import subprocess, json, boto3;\
from gitops_summary._version import __version__;\
from gitops_summary.model import load_model_id;\
current = __version__;\
log = subprocess.check_output(['git', 'log', '--reverse', '--format=%H %s%n%b---', 'v' + current + '..HEAD'], text=True) if subprocess.run(['git', 'rev-parse', 'v' + current], capture_output=True).returncode == 0 else subprocess.check_output(['git', 'log', '--reverse', '--format=%H %s%n%b---', '--all'], text=True);\
version_content = open('VERSION').read();\
model_id = load_model_id();\
prompt = f'''You are a release manager. The current version is {current}.\n\nHere are the NEW commits since last release:\n\n{log}\n\nHere is the current VERSION file:\n\n{version_content}\n\nAnalyze the commits and determine:\n1. What the next version should be (following semver: breaking=major, feature=minor, fix=patch)\n2. A changelog entry for the new version\n\nRespond with ONLY a JSON object (no markdown fencing) with keys:\n- \"new_version\": the new semver string\n- \"changelog_entry\": the full changelog block to insert (starting with ## X.Y.Z header, using ### Added/Changed/Fixed/Breaking subsections)\n''';\
client = boto3.client('bedrock-runtime', region_name='us-east-1');\
body = json.dumps({'anthropic_version': 'bedrock-2023-05-01', 'max_tokens': 2048, 'messages': [{'role': 'user', 'content': prompt}]});\
resp = client.invoke_model(modelId=model_id, body=body);\
result = json.loads(json.loads(resp['body'].read())['content'][0]['text']);\
new_ver = result['new_version'];\
entry = result['changelog_entry'];\
lines = open('VERSION').readlines();\
with open('VERSION', 'w') as f:\
    f.write(new_ver + '\n');\
    f.write('\n');\
    f.write('# Semantic Versioning Changelog\n');\
    f.write('# See https://semver.org/\n');\
    f.write('\n');\
    f.write(entry.rstrip() + '\n\n');\
    found_header = False;\
    for line in lines[1:]:\
        if not found_header and line.strip() in ('', '# Semantic Versioning Changelog', '# See https://semver.org/'):\
            continue;\
        found_header = True;\
        f.write(line);\
import subprocess;\
subprocess.run(['sed', '-i', f's/__version__ = \".*\"/__version__ = \"{new_ver}\"/', 'src/gitops_summary/_version.py']);\
print(f'Version bumped: {current} -> {new_ver}');\
print(f'Changelog entry added. Review VERSION file before committing.');\
"
