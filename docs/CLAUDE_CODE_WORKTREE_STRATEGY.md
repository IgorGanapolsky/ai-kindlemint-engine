# Claude Code Worktree Strategy

## 🎯 Simple & Effective Git Worktree Setup for Claude Code

Based on Anthropic's recommendations and real-world usage, this is a **simplified worktree strategy** that actually works.

## ✅ The 3-Worktree Strategy

We maintain exactly **3 worktrees** for different purposes:

```
ai-kindlemint-engine/          # Main repository (current features)
├── worktrees/
│   ├── main/                  # Clean main branch for hotfixes
│   └── experiments/           # Experimental features
```

### 1. **Main Directory** (`/ai-kindlemint-engine`)
- Your active development
- Feature branches
- Current work

### 2. **Main Worktree** (`/worktrees/main`)
- Always on main branch
- For emergency hotfixes
- Clean state for comparisons

### 3. **Experiments Worktree** (`/worktrees/experiments`)
- Testing risky changes
- AI experiments
- Throwaway work

## 🛠️ Setup Commands

```bash
# One-time setup
mkdir -p worktrees
git worktree add worktrees/main main
git worktree add worktrees/experiments -b experiments

# Verify setup
git worktree list
```

## 📋 Claude Code Best Practices

### 1. **Parallel Work**
Claude can work in different worktrees simultaneously:
- Fix bugs in `worktrees/main`
- While developing features in main directory
- Test experiments in `worktrees/experiments`

### 2. **Context Switching**
```bash
# Quick switch for hotfix
cd worktrees/main
git pull origin main
# Make fixes
git push

# Back to feature work
cd ../..
```

### 3. **Cleanup**
```bash
# Remove experiment when done
git worktree remove worktrees/experiments
# Recreate when needed
git worktree add worktrees/experiments -b new-experiment
```

## ❌ What NOT to Do

1. **Don't create 10+ worktrees** - It's confusing and breaks things
2. **Don't nest worktrees** inside each other
3. **Don't use worktrees for every feature** - Regular branches work fine
4. **Don't share worktrees** between different repositories

## 🎯 When to Use Worktrees

### ✅ Good Use Cases:
- Emergency hotfixes while developing
- Testing destructive changes
- Comparing implementations side-by-side
- Running long processes without blocking development

### ❌ Bad Use Cases:
- Every feature branch (overkill)
- CI/CD automation (too complex)
- Team collaboration (use regular branches)

## 🚀 Quick Reference

```bash
# List worktrees
git worktree list

# Add worktree
git worktree add worktrees/[name] [branch]

# Remove worktree
git worktree remove worktrees/[name]

# Clean up
git worktree prune
```

## 💡 Pro Tips

1. **Keep it simple** - 3 worktrees maximum
2. **Name clearly** - Use descriptive names
3. **Clean regularly** - Remove unused worktrees
4. **Document usage** - Note which worktree is for what

This strategy gives you the benefits of worktrees without the complexity!