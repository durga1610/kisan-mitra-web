# Repository Configuration Guide — GitHub Pages Reports

This guide describes how to configure the repository to host E2E test reports online.

## 1. Configure GitHub Pages deployment source
By default, GitHub Pages expects code to be built from a branch. Since our workflow dynamically builds, compiles, and deploys pages directly from the GitHub Actions runners, we must switch the Pages source to **GitHub Actions**.

### Step-by-Step Instructions:
1. Open your repository on GitHub: `https://github.com/durga1610/kisan-mitra-web`
2. Go to **Settings** (tab on the top navigation bar).
3. Select **Pages** from the left sidebar (under "Code and automation").
4. Under **Build and deployment** > **Source**, click the dropdown and change the selection from "Deploy from a branch" to **GitHub Actions**.

---

## 2. Set Workflow Permissions
The workflow needs permission to commit report assets to the repository and write to GitHub Pages.

### Step-by-Step Instructions:
1. Go to **Settings** > **Actions** > **General** (in the left sidebar).
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Check **Allow GitHub Actions to create and approve pull requests**.
5. Click **Save**.
