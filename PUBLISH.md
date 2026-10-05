# Publishing a clean copy

The project repository is [Djancer/scan-everything](https://github.com/Djancer/scan-everything).
Publish only the headless example; do not change or upload a private LUX installation.

If a GitHub integration returns `403 Resource not accessible by integration`, it
does not have the required write access. Options for publishing your own clean copy:

1. Grant the integration repository/content write access, then retry. Do not paste a personal access token into chat.
2. Sign into GitHub as the owner and upload the audited files, preserving folder structure.
3. Use Git locally after unpacking and reviewing the publication set.

For a new clean folder and a new empty remote, replace YOUR_ACCOUNT with your account:

```powershell
git init -b main
git add .
git diff --cached --stat
git diff --cached
git commit -m "Add local Qwen document processing example and guides"
git remote add origin https://github.com/YOUR_ACCOUNT/scan-everything.git
git push -u origin main
```

Do not run this sequence inside a private installation. Git may request author
name/email and authentication; provide your own details without publishing secrets.
If the remote already has content, inspect it first. Do not force-push.

Uploading `.github/workflows/tests.yml` may require workflow-write permission
depending on the authentication method. Do not disable account protection to upload.
After publication, verify README, its language links, guides, SKILL.md, and Actions.
Model weights, OCR/Python runtimes, personal documents, and private UI assets must stay out.

No source license has been selected yet. A separate GitHub Pages website is not
required: README is the project landing page, and HTML is intentionally excluded.
