# Development Tools Migration Plan

## Current Status (2025-11-14)

---

## Remaining Tasks

### Phase 5: CI/CD (Docker) - 25% remaining

#### 5.2 CI for Docker Publishing
- [ ] Create `.github/workflows/docker-publish.yml`
- [ ] Configure triggers:
  - On tag push (e.g., v1.2.0)
  - On GitHub release
- [ ] Workflow steps:
  - Build Docker image
  - Tag with version (from git tag or pyproject.toml)
  - Push to Docker Hub or GitHub Container Registry
  - Create multiple tags (latest, version, version-major)
- [ ] Create `Dockerfile` if necessary
- [ ] Configure GitHub secrets:
  - `DOCKER_USERNAME`
  - `DOCKER_TOKEN` or `GITHUB_TOKEN`

### Phase 6: Adding Sensitive Data Encryption - 100% ✅

#### 6.1 Encryption Feature Design ✅
- [x] Choose encryption library (cryptography recommended)
- [x] Define architecture:
  - Symmetric encryption (Fernet - AES-128 CBC with HMAC)
  - Encryption key stored in Django settings
  - `enable_cypher` field in Parameter model
  - Transparent encryption/decryption on set/get
- [x] Plan migration to add `enable_cypher` field

#### 6.2 Encryption Implementation ✅
- [x] Add `cryptography` to dependencies
- [x] Create encryption functions in `utils.py`:
  - `encrypt_value(value: str, encryption_key: str | bytes | None = None) -> str`
  - `decrypt_value(encrypted_value: str, encryption_key: str | bytes | None = None) -> str`
  - `get_encryption_key(key: str | bytes | None = None)` - retrieves key from settings or uses provided key
- [x] Add `enable_cypher` field to Parameter model (BooleanField)
- [x] Create Django migration (0006_parameter_enable_cypher.py)
- [x] Modify model methods:
  - `set_*()` methods - encrypt value if `enable_cypher=True`
  - `get()`, `str()`, `int()`, `float()`, etc. - automatically decrypt if `enable_cypher=True`
  - `to_dict()` - exports decrypted values
- [x] Add `dap_rotate_key` management command for key rotation (two-step process)
- [x] Add encryption field to Django admin
- [x] Write comprehensive tests (12 encryption tests + 10 rotation tests)
- [x] Document encryption feature (merged into docs/management-commands.md)

#### 6.3 TODO: Make cryptography dependency optional
- [ ] Update `pyproject.toml` to make `cryptography` an optional dependency
  - Add `[tool.poetry.extras]` section with `cryptography = ["cryptography"]`
  - Users can install with: `pip install django-app-parameter[cryptography]`
  - Or with poetry: `poetry add django-app-parameter[cryptography]`
- [ ] Update installation documentation to mention optional cryptography dependency
- [ ] Add runtime check in encryption functions to provide clear error if cryptography not installed
- [ ] Explore how to update Tox config to test both with and without cryptography installed


---

## Recommended Next Steps

### Medium Priority (features)
5. **Docker Workflow** - If containerization is needed
6. **Phase 6: Encryption** - Important security feature


