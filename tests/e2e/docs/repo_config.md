# Repository Configuration Guide — Web Pages Deployment

This guide describes how to configure the repository to build and host the Flutter web client and test results.

## 1. Configure GitHub Pages deployment source
By default, GitHub Pages expects code to be built from a branch. Since our workflow dynamically builds, compiles, and deploys pages directly from the GitHub Actions runners, we must switch the Pages source to **GitHub Actions**.

### Step-by-Step Instructions:
1. Open your repository on GitHub: `https://github.com/durga1610/kisan-mitra-web`
2. Go to **Settings** (tab on the top navigation bar).
3. Select **Pages** from the left sidebar (under "Code and automation").
4. Under **Build and deployment** > **Source**, click the dropdown and change the selection from "Deploy from a branch" to **GitHub Actions**.

---

## 2. Environment Variables & Secrets
The E2E suite consumes a target URL using:
* **BASE_URL**: Configurable parameter set in the GitHub Actions runner environment. It resolves to your GitHub Pages domain:
  `https://<github-username>.github.io/<repository-name>/`
