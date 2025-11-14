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

### Phase 6: Adding Sensitive Data Encryption - 0%

#### 6.1 Encryption Feature Design
- [ ] Choose encryption library (cryptography recommended)
- [ ] Define architecture:
  - Symmetric encryption (AES-256)
  - Encryption key stored in Django settings
  - `is_encrypted` field in Parameter model
  - Transparent encryption/decryption on get/set
- [ ] Plan migration to add `is_encrypted` field

#### 6.2 Encryption Implementation
- [ ] Add `cryptography` to dependencies
- [ ] Create `encryption.py` module with functions:
  - `encrypt_value(value: str, key: str) -> str`
  - `decrypt_value(encrypted_value: str, key: str) -> str`
  - `get_encryption_key()` - retrieves key from settings
- [ ] Add `is_encrypted` field to Parameter model (BooleanField)
- [ ] Create Django migration
- [ ] Modify model methods:
  - `save()` - encrypt if `is_encrypted=True`
  - `get()` - automatically decrypt if needed
  - `str()`, `int()`, `float()`, etc. - decryption support


---

## Recommended Next Steps

### Medium Priority (features)
5. **Docker Workflow** - If containerization is needed
6. **Phase 6: Encryption** - Important security feature


