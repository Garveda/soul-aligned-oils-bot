# 🔗 Connect to Existing GitHub Repository

Your local git is already initialized. Follow these steps to connect to your existing GitHub repository.

---

## Step 1: Check Current Remote (Optional)

First, let's see if a remote is already configured:

```powershell
git remote -v
```

If you see a remote URL, you can either:
- **Update it** if it's pointing to the wrong repository
- **Skip to Step 3** if it's correct

---

## Step 2: Add GitHub Remote

Replace `YOUR_USERNAME` and `REPOSITORY_NAME` with your actual GitHub details:

```powershell
# Add your GitHub repository as remote origin
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
```

**If you get "remote origin already exists" error:**
```powershell
# Remove existing remote first
git remote remove origin

# Then add the correct one
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
```

**Example:**
If your repository is `https://github.com/johndoe/soul-aligned-oils-bot`, use:
```powershell
git remote add origin https://github.com/johndoe/soul-aligned-oils-bot.git
```

---

## Step 3: Stage and Commit Your Files

Make sure all your files are committed:

```powershell
# Check what files need to be added
git status

# Add all files (respects .gitignore)
git add .

# Commit if you have uncommitted changes
git commit -m "Initial commit - Soul Aligned Oils Bot"
```

---

## Step 4: Push to GitHub

Push your code to the existing repository:

```powershell
# Set main branch (if not already)
git branch -M main

# Push to GitHub
git push -u origin main
```

**If the repository already has commits:**
If your GitHub repository already has some files (like a README), you may need to pull first:

```powershell
# Pull and merge existing content
git pull origin main --allow-unrelated-histories

# Resolve any conflicts if needed, then:
git push -u origin main
```

---

## Step 5: Verify Connection

Check that everything is connected:

```powershell
# Verify remote is set correctly
git remote -v

# Check status
git status
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git (fetch)
origin  https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git (push)
```

---

## 🔐 Authentication

**If you get authentication errors:**

GitHub requires a **Personal Access Token** instead of a password:

1. Go to: https://github.com/settings/tokens
2. Click: **"Generate new token"** → **"Generate new token (classic)"**
3. Name it: `Soul Aligned Oils Bot`
4. Select scope: **`repo`** (full control of private repositories)
5. Click: **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)
7. When prompted for password during `git push`, paste the token instead

---

## ✅ Success!

Once connected, you can:

**Push updates:**
```powershell
git add .
git commit -m "Your update message"
git push
```

**Check status:**
```powershell
git status
```

**View commit history:**
```powershell
git log --oneline
```

---

## 🚂 Next: Connect to Railway

After your code is on GitHub, you can connect Railway:

1. Go to: https://railway.app
2. Sign in with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Select your repository
5. Add environment variables (see `GITHUB_RAILWAY_SETUP.md`)

---

**Need your repository URL?** 
- Go to your GitHub repository page
- Click the green **"Code"** button
- Copy the HTTPS URL
- Use that URL in Step 2 above
