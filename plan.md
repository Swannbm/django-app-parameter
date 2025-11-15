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

#### 6.3 Make cryptography dependency optional ✅
- [x] Update `pyproject.toml` to make `cryptography` an optional dependency
  - Add `[tool.poetry.extras]` section with `cryptography = ["cryptography"]`
  - Users can install with: `pip install django-app-parameter[cryptography]`
  - Or with poetry: `poetry add django-app-parameter[cryptography]`
- [x] Update installation documentation to mention optional cryptography dependency
  - Updated README.md Install section
  - Updated docs/README.md Quick Start and Encryption sections
- [x] Add runtime check in encryption functions to provide clear error if cryptography not installed
  - Added try/except import with HAS_CRYPTOGRAPHY flag in utils.py
  - Added runtime check in get_encryption_key() function
  - Added runtime check in dap_rotate_key command
- [x] Update Tox config to include cryptography in test environments
  - Added cryptography>=46.0.0 to all test environments (testenv, pyright, coverage, dev)


---

## Recommended Next Steps

### Medium Priority (features)
5. **Docker Workflow** - If containerization is needed
6. **Phase 6: Encryption** - Important security feature

---

## Phase 7: Documentation automatique avec Sphinx et Read the Docs

### Objectif
Générer automatiquement la documentation à partir du code Python et la publier sur Read the Docs.

### 7.1 Configuration de Sphinx
- [ ] Ajouter les dépendances à `pyproject.toml` (groupe dev) :
  - `sphinx` : moteur de documentation
  - `sphinx-rtd-theme` : thème Read the Docs
  - `sphinx-autodoc-typehints` : documentation des types Python
  - `myst-parser` : support Markdown
- [ ] Initialiser la configuration Sphinx dans `docs/` :
  - Créer `docs/conf.py` avec la configuration
  - Créer `docs/index.rst` (page d'accueil)
  - Créer `docs/api.rst` (documentation API auto-générée)
- [ ] Migrer/intégrer les fichiers Markdown existants :
  - `docs/README.md`
  - `docs/usage-guide.md`
  - `docs/management-commands.md`
  - `docs/faq.md`

### 7.2 Documentation automatique de l'API
- [ ] Configurer `sphinx.ext.autodoc` pour extraire les docstrings
- [ ] Vérifier/améliorer les docstrings existantes dans :
  - `django_app_parameter/models.py`
  - `django_app_parameter/utils.py`
  - `django_app_parameter/admin.py`
  - `django_app_parameter/context_processors.py`
  - Commandes de gestion (`management/commands/`)
- [ ] Créer la structure de documentation API :
  - Documentation des modèles
  - Documentation des fonctions utilitaires
  - Documentation des commandes de gestion

### 7.3 Configuration Read the Docs
- [ ] Créer `.readthedocs.yaml` à la racine du projet
- [ ] Configurer la construction de la documentation :
  - Version Python
  - Dépendances à installer
  - Commande de build Sphinx
- [ ] S'inscrire sur readthedocs.org
- [ ] Importer le projet GitHub
- [ ] Vérifier la première construction

### 7.4 Amélioration de la documentation
- [ ] Ajouter un Makefile pour générer la doc localement
- [ ] Ajouter des exemples de code
- [ ] Créer un changelog intégré
- [ ] Ajouter des badges (ReadTheDocs, Coverage, etc.) au README


