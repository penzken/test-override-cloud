# CRM Overrides

Custom Frappe CRM app that provides backend and frontend overrides without modifying core CRM code.

---

## 📚 Documentation

**New to the project?** Start here:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[QUICK_START.md](../../QUICK_START.md)** | Get productive in 5 minutes | ⚡ 5 min |
| **[PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md)** | Understand project layout | 📁 10 min |
| **[CUSTOMIZATIONS.md](../../CUSTOMIZATIONS.md)** | See what's customized | 📋 15 min |
| **[OVERRIDE_GUIDE.md](OVERRIDE_GUIDE.md)** | Technical deep-dive | 🔧 30 min |

---

## 🎯 What This App Does

This app customizes Frappe CRM by:

### Backend (Python)
- **Custom List Views**: Modified columns for Leads and Deals
- **Field Layouts**: Customized form field arrangements
- **Business Logic**: Extended DocType controllers

### Frontend (Vue.js)
- **Custom Components**: Styled list views and pages
- **Visual Enhancements**: Icons, colors, formatting
- **Custom Routing**: Modified navigation flow

**Key Principle**: All customizations are isolated in this app. The core CRM remains untouched and upgradeable.

---

## 🚀 Quick Start

### For Developers:

```bash
# 1. Backend changes: Edit Python files
nano crm_overrides/overrides/crm_lead.py

# 2. Restart to apply
bench restart

# 3. Frontend changes: Edit Vue files
nano frontend/src_overrides/components/ListViews/LeadsListView.vue

# 4. Build frontend
cd frontend
yarn build

# 5. Restart again
bench restart
```

👉 **See [QUICK_START.md](../../QUICK_START.md) for detailed instructions**

---

## 📦 Installation

### Prerequisites
- Frappe Framework installed
- CRM app installed
- Node.js and Yarn (for frontend)

### Install This App

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app crm_overrides
```

### Build Frontend

```bash
cd apps/crm_overrides/frontend
yarn install
yarn build
```

### Restart Bench

```bash
bench restart
```

---

## 🏗️ Project Structure

```
crm_overrides/
├── crm_overrides/              # Python backend
│   ├── overrides/              # DocType controller overrides
│   │   ├── crm_lead.py        # Lead customizations
│   │   ├── crm_deal.py        # Deal customizations
│   │   └── fields_layout.py   # Form layout overrides
│   ├── hooks.py                # App configuration
│   └── www/                    # Web routes
│
└── frontend/                   # Vue.js frontend
    ├── src_overrides/          # Custom Vue components
    │   ├── components/
    │   └── pages/
    └── custom-build.mjs        # Build script
```

---

## 🛠️ Current Customizations

### Backend
- ✅ CRM Lead list columns customized
- ✅ CRM Deal list columns customized
- ✅ Deal form fields layout modified
- ✅ Annual revenue → Deal value replacement

### Frontend
- ✅ Lead list visual styling (green, bold, emoji)
- ✅ Organization page customized
- ✅ Custom routing configuration

👉 **See [CUSTOMIZATIONS.md](../../CUSTOMIZATIONS.md) for complete details**

---

## 🧪 Development Workflow

### Making Changes

1. **Backend Changes**:
   ```bash
   # Edit Python file → bench restart → Test
   ```

2. **Frontend Changes**:
   ```bash
   # Edit Vue file → yarn build → bench restart → Test
   ```

### Testing

- Navigate to affected page in browser
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Check browser console for errors (F12)

### Before Committing

- [ ] Test thoroughly
- [ ] Update documentation
- [ ] Run code formatters
- [ ] Create clear commit message

---

## 🔧 Contributing

This app uses `pre-commit` for code formatting and linting.

### Setup Pre-commit

```bash
cd apps/crm_overrides
pre-commit install
```

### Tools Used
- **Python**: ruff, pyupgrade
- **JavaScript**: eslint, prettier

### Contribution Guidelines

1. Read [QUICK_START.md](../../QUICK_START.md)
2. Create feature branch: `git checkout -b feature/my-change`
3. Make changes in `apps/crm_overrides/` only
4. Test thoroughly
5. Update [CUSTOMIZATIONS.md](../../CUSTOMIZATIONS.md)
6. Commit with clear message
7. Create pull request
8. Get code review

**Important**: Never modify files in `apps/frappe/` or `apps/crm/`.

---

## 📖 Documentation Guide

| File | When to Read |
|------|--------------|
| [QUICK_START.md](../../QUICK_START.md) | Starting work, common tasks |
| [PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) | Understanding architecture |
| [CUSTOMIZATIONS.md](../../CUSTOMIZATIONS.md) | What exists, how to modify |
| [OVERRIDE_GUIDE.md](OVERRIDE_GUIDE.md) | Deep technical understanding |
| [FRONTEND_OVERRIDE_COMPLETE.md](FRONTEND_OVERRIDE_COMPLETE.md) | Frontend build details |

---

## 🐛 Troubleshooting

### Changes Not Appearing?
```bash
# 1. Restart bench
bench restart

# 2. Clear browser cache (Ctrl+Shift+R)

# 3. For frontend: rebuild
cd frontend && yarn build && bench restart
```

### Build Errors?
```bash
# Clean rebuild
cd frontend
rm -rf node_modules src
yarn install
yarn build
```

### Check What's Overridden
```bash
bench console
>>> frappe.get_hooks('override_doctype_class')
```

👉 **See [QUICK_START.md](../../QUICK_START.md#troubleshooting) for more**

---

## 📞 Getting Help

1. Check documentation first
2. Search existing code for examples
3. Check bench logs: `bench --verbose`
4. Ask team members
5. Create detailed issue

---

## 📄 License

MIT

---

## 👥 Maintainers

**Author**: Thang (lethang507@gmail.com)  
**Team**: Development Team  
**Last Updated**: November 2025

---

## 🔗 Related Resources

- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Frappe CRM Repository](https://github.com/frappe/crm)
- [Vue.js Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)

---

**Ready to start?** → [QUICK_START.md](../../QUICK_START.md) 🚀
