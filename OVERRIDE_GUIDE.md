# CRM Override Guide

A comprehensive guide for overriding Frappe CRM functionality using the `crm_overrides` custom app.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Python Backend Override](#python-backend-override)
- [Frontend Vue.js Override](#frontend-vuejs-override)
- [Build Process](#build-process)
- [Usage](#usage)
- [Adding More Overrides](#adding-more-overrides)

---

## Overview

This guide explains how to override both backend (Python) and frontend (Vue.js) functionality in Frappe CRM without modifying the core CRM app. This approach ensures:

- ✅ **Maintainability**: Core CRM updates won't break your customizations
- ✅ **Modularity**: All customizations are isolated in a separate app
- ✅ **Upgrade Safety**: Easy to maintain during Frappe/CRM version upgrades
- ✅ **Clean Architecture**: Only override what you need

---

## Architecture

### Directory Structure

```
apps/crm_overrides/
├── crm_overrides/
│   ├── overrides/               # Python overrides
│   │   ├── __init__.py
│   │   └── crm_lead.py         # Custom CRM Lead class
│   ├── www/                     # Web routes
│   │   └── crm.py              # CRM route handler
│   ├── hooks.py                 # App configuration
│   └── public/                  # Built frontend assets
│       └── frontend/
└── frontend/                    # Frontend source
    ├── src_overrides/          # Custom Vue components
    │   └── components/
    │       └── ListViews/
    │           └── LeadsListView.vue
    ├── src/                     # Auto-generated (build time)
    ├── custom-build.mjs        # Build script
    ├── vite.config.js          # Vite configuration
    └── package.json            # Dependencies
```

---

## Python Backend Override

### Example: Adding Annual Revenue Column to Leads List

#### Step 1: Create Override Class

**File**: `crm_overrides/overrides/crm_lead.py`

```python
from crm.fcrm.doctype.crm_lead.crm_lead import CRMLead


class CustomCRMLead(CRMLead):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Name",
                "type": "Data",
                "key": "lead_name",
                "width": "12rem",
            },
            {
                "label": "Organization",
                "type": "Link",
                "key": "organization",
                "options": "CRM Organization",
                "width": "10rem",
            },
            {
                "label": "Status",
                "type": "Select",
                "key": "status",
                "width": "8rem",
            },
            {
                "label": "Annual Revenue",
                "type": "Currency",
                "key": "annual_revenue",
                "width": "10rem",
            },
            {
                "label": "Email",
                "type": "Data",
                "key": "email",
                "width": "12rem",
            },
            {
                "label": "Mobile No",
                "type": "Data",
                "key": "mobile_no",
                "width": "11rem",
            },
            {
                "label": "Assigned To",
                "type": "Text",
                "key": "_assign",
                "width": "10rem",
            },
            {
                "label": "Last Modified",
                "type": "Datetime",
                "key": "modified",
                "width": "8rem",
            },
        ]
        rows = [
            "name",
            "lead_name",
            "organization",
            "status",
            "annual_revenue",  # Added to fetch this data
            "email",
            "mobile_no",
            "lead_owner",
            "first_name",
            "sla_status",
            "response_by",
            "first_response_time",
            "first_responded_on",
            "modified",
            "_assign",
            "image",
        ]
        return {"columns": columns, "rows": rows}
```

#### Step 2: Register Override in Hooks

**File**: `crm_overrides/hooks.py`

```python
# DocType Class Override
# This is a standard Frappe Framework hook for overriding DocType controllers
# Source: frappe/frappe/model/base_document.py (line 111)
override_doctype_class = {
    "CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead",
}
```

**How It Works**:
- This hook is defined in Frappe Framework core: `frappe/model/base_document.py`
- When Frappe loads a DocType controller, it calls `frappe.get_hooks("override_doctype_class")` (line 111)
- If an override exists, it loads your custom class instead of the original (lines 117-128)
- Your custom class **must** inherit from the original class (verified at line 122)
- This is the **official Frappe way** to extend DocType behavior

**Real Examples**:
- CRM app itself uses this to override Contact and Email Template (see `apps/crm/crm/hooks.py` lines 134-137)
- ERPNext uses this extensively to extend Frappe core doctypes

#### Step 3: Restart Frappe

```bash
bench restart
```

### How Backend Override Works (Detailed)

#### Step 1: Frontend API Call
**Location**: `apps/crm/frontend/src/components/ViewControls.vue` (line 507-534)

```javascript
list.value = createResource({
  url: 'crm.api.doc.get_data',  // Calls backend API
  params: {
    doctype: 'CRM Lead',
    filters: {...},
    order_by: 'modified desc',
    view: {
      custom_view_name: '',
      view_type: 'list',
      group_by_field: 'owner'
    },
    columns: '',  // Empty = use default
    rows: '',     // Empty = use default
    page_length: 20,
    page_length_count: 20
  },
})
```

**What Happens**:
- Vue component creates a resource (Frappe UI's data fetching mechanism)
- Makes HTTP POST to `/api/method/crm.api.doc.get_data`
- Sends parameters including doctype name, filters, and view settings
- Empty `columns` and `rows` means "use default from DocType"

#### Step 2: Backend API Endpoint
**Location**: `apps/crm/crm/api/doc.py`

```python
@frappe.whitelist()
def get_data(doctype, filters=None, order_by=None, ...):
    """Main API endpoint for fetching list data"""
    
    # Get the DocType controller class
    controller = frappe.get_doc(doctype, {})  # Creates instance
    
    # If no columns/rows specified, get defaults
    if not columns or not rows:
        default_data = controller.default_list_data()  # ← CALLS YOUR OVERRIDE!
        columns = default_data.get('columns', [])
        rows = default_data.get('rows', [])
    
    # Fetch actual data from database
    data = frappe.get_list(
        doctype,
        fields=rows,  # Uses rows from default_list_data()
        filters=filters,
        order_by=order_by,
        limit_page_length=page_length
    )
    
    return {
        'data': data,
        'columns': columns,
        'rows': rows,
        'total_count': total,
        'page_length': page_length
    }
```

#### Step 3: Override Resolution (The Magic!)
**Location**: `apps/frappe/frappe/model/base_document.py` (line 111-128)

When `frappe.get_doc('CRM Lead', {})` is called:

```python
# 1. Frappe needs to load the controller class
def get_controller(doctype):
    return import_controller(doctype)

# 2. Import controller checks for overrides
def import_controller(doctype):
    # Load original class first
    from crm.fcrm.doctype.crm_lead.crm_lead import CRMLead
    class_ = CRMLead
    
    # Check if override exists
    class_overrides = frappe.get_hooks("override_doctype_class")
    # Returns: {"CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead"}
    
    if class_overrides and class_overrides.get("CRM Lead"):
        # Import path: "crm_overrides.overrides.crm_lead.CustomCRMLead"
        import_path = class_overrides["CRM Lead"][-1]
        
        # Split into module and class name
        # module_path = "crm_overrides.overrides.crm_lead"
        # custom_classname = "CustomCRMLead"
        module_path, custom_classname = import_path.rsplit(".", 1)
        
        # Import your custom module
        custom_module = frappe.get_module(module_path)
        # custom_module = crm_overrides.overrides.crm_lead
        
        # Get your custom class
        custom_class_ = getattr(custom_module, custom_classname, None)
        # custom_class_ = CustomCRMLead
        
        # Validate inheritance (MUST inherit from original)
        if not issubclass(custom_class_, class_):
            frappe.throw("CustomCRMLead must inherit from CRMLead!")
        
        # REPLACE original with custom class!
        class_ = custom_class_  # ← Now using YOUR class
    
    return class_
```

**Result**: Any call to `frappe.get_doc('CRM Lead', ...)` now creates a `CustomCRMLead` instance instead of `CRMLead`!

#### Step 4: Call Your Override Method

```python
# In the API, this line:
controller = frappe.get_doc('CRM Lead', {})
# Actually creates: CustomCRMLead instance

# Then this line:
default_data = controller.default_list_data()
# Calls: CustomCRMLead.default_list_data()  ← YOUR METHOD!

# Returns:
{
    'columns': [
        {'label': 'Name', 'key': 'lead_name', ...},
        {'label': 'Status', 'key': 'status', ...},
        {'label': 'Annual Revenue', 'key': 'annual_revenue', ...},  # ← YOUR ADDITION
        {'label': 'Email', 'key': 'email', ...},
        ...
    ],
    'rows': [
        'name', 'lead_name', 'status', 'annual_revenue', 'email', ...  # ← YOUR ADDITION
    ]
}
```

#### Step 5: Database Query

```python
# API uses the rows array to fetch data
data = frappe.get_list(
    'CRM Lead',
    fields=[
        'name',
        'lead_name', 
        'status',
        'annual_revenue',  # ← Fetched because it's in your rows array
        'email',
        'mobile_no',
        ...
    ],
    filters=filters,
    order_by='modified desc',
    limit_page_length=20
)

# SQL Generated (approximately):
"""
SELECT 
    name, 
    lead_name, 
    status, 
    annual_revenue,  -- ← Included in query
    email, 
    mobile_no,
    ...
FROM `tabCRM Lead`
WHERE converted = 0
ORDER BY modified DESC
LIMIT 20
"""
```

#### Step 6: Backend Response

```json
{
  "data": [
    {
      "name": "LEAD-2024-00001",
      "lead_name": "John Doe",
      "status": "Open",
      "annual_revenue": 1000000.00,  // ← Your data
      "email": "john@example.com",
      ...
    },
    {
      "name": "LEAD-2024-00002",
      "lead_name": "Jane Smith",
      "status": "Contacted",
      "annual_revenue": 500000.00,  // ← Your data
      "email": "jane@example.com",
      ...
    }
  ],
  "columns": [
    {
      "label": "Name",
      "type": "Data",
      "key": "lead_name",
      "width": "12rem"
    },
    {
      "label": "Annual Revenue",  // ← Your column definition
      "type": "Currency",
      "key": "annual_revenue",
      "width": "10rem"
    },
    ...
  ],
  "rows": ["name", "lead_name", "status", "annual_revenue", ...],
  "total_count": 150,
  "page_length": 20
}
```

#### Step 7: Frontend Processing
**Location**: `apps/crm/frontend/src/pages/Leads.vue` (lines 348-362)

```javascript
// Computed property processes the raw data
const rows = computed(() => {
  if (!leads.value?.data?.data) return []
  
  // leads.value.data.data = [{name: "LEAD-001", annual_revenue: 1000000, ...}, ...]
  // leads.value.data.columns = [{key: 'annual_revenue', type: 'Currency', ...}, ...]
  
  return parseRows(leads.value.data.data, leads.value.data.columns)
})

function parseRows(rows, columns) {
  return rows.map((lead) => {
    let _rows = {}
    
    // For each field in the response
    leads.value.data.rows.forEach((row) => {
      _rows[row] = lead[row]
      
      // Find column definition
      let fieldType = columns?.find((col) => col.key == row)?.type
      
      // Format Currency fields
      if (fieldType && fieldType == 'Currency') {
        // annual_revenue: 1000000 → "$1,000,000.00"
        _rows[row] = getFormattedCurrency(row, lead)
      }
      
      // Format Date fields
      if (fieldType && ['Date', 'Datetime'].includes(fieldType)) {
        _rows[row] = formatDate(lead[row], '', true)
      }
    })
    
    return _rows
  })
}
```

**Result**: 
```javascript
[
  {
    name: "LEAD-2024-00001",
    lead_name: { label: "John Doe", image: "...", ... },
    status: { label: "Open", color: "green" },
    annual_revenue: "$1,000,000.00",  // ← Formatted!
    email: { label: "john@example.com" },
    ...
  },
  ...
]
```

#### Step 8: Component Rendering
**Location**: `apps/crm/frontend/src/pages/Leads.vue` (lines 232-254)

```vue
<LeadsListView
  :rows="rows"                          ← Formatted data
  :columns="leads.data.columns"         ← Column definitions with annual_revenue
  :options="{
    showTooltip: false,
    resizeColumn: true,
    rowCount: 150,
    totalCount: 150,
  }"
/>
```

#### Step 9: Table Display
**Location**: `apps/crm/frontend/src/components/ListViews/LeadsListView.vue`

```vue
<template>
  <ListView :columns="columns" :rows="rows">
    <!-- Header -->
    <ListHeader>
      <ListHeaderItem 
        v-for="column in columns" 
        :key="column.key"
        :item="column"
      >
        <!-- Renders: Name | Organization | Status | Annual Revenue | Email | ... -->
      </ListHeaderItem>
    </ListHeader>
    
    <!-- Body -->
    <ListRows :rows="rows">
      <!-- For each row in rows -->
      <ListRow v-for="row in rows" :row="row">
        <!-- For each column, render the cell -->
        <div v-if="column.key === 'annual_revenue'">
          {{ row.annual_revenue }}  <!-- Displays: $1,000,000.00 -->
        </div>
      </ListRow>
    </ListRows>
  </ListView>
</template>
```

### Complete Flow Summary

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. FRONTEND REQUEST                                              │
│    ViewControls.vue → POST /api/method/crm.api.doc.get_data     │
│    Params: {doctype: 'CRM Lead', columns: '', rows: ''}         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 2. BACKEND API HANDLER                                           │
│    crm.api.doc.get_data() function                              │
│    └─> controller = frappe.get_doc('CRM Lead', {})              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 3. OVERRIDE RESOLUTION (Frappe Core)                            │
│    base_document.import_controller()                             │
│    ├─> Load original: CRMLead                                   │
│    ├─> Check hooks: override_doctype_class                      │
│    ├─> Found override: CustomCRMLead                            │
│    ├─> Validate: issubclass(CustomCRMLead, CRMLead) ✓          │
│    └─> Return: CustomCRMLead (YOUR CLASS)                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 4. CALL YOUR METHOD                                              │
│    controller.default_list_data()                                │
│    └─> CustomCRMLead.default_list_data()                        │
│        Returns: {                                                │
│          columns: [..., {key: 'annual_revenue'}, ...],          │
│          rows: [..., 'annual_revenue', ...]                     │
│        }                                                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 5. DATABASE QUERY                                                │
│    frappe.get_list('CRM Lead', fields=rows, ...)                │
│    SQL: SELECT name, lead_name, annual_revenue, ... FROM ...    │
│    Returns: [{annual_revenue: 1000000, ...}, ...]              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 6. API RESPONSE                                                  │
│    Return JSON: {                                                │
│      data: [...],                                                │
│      columns: [..., annual_revenue column, ...],                │
│      rows: [..., 'annual_revenue', ...]                         │
│    }                                                             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 7. FRONTEND PROCESSING                                           │
│    Leads.vue parseRows()                                         │
│    ├─> Format currency: 1000000 → "$1,000,000.00"              │
│    ├─> Format dates                                             │
│    └─> Build display objects                                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 8. PASS TO LIST COMPONENT                                        │
│    <LeadsListView                                                │
│      :rows="formattedRows"                                       │
│      :columns="columnsWithAnnualRevenue"                        │
│    />                                                            │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 9. RENDER TABLE                                                  │
│    LeadsListView.vue                                             │
│    ┌────────┬──────────┬────────┬─────────────────┬────────┐   │
│    │ Name   │ Org      │ Status │ Annual Revenue  │ Email  │   │
│    ├────────┼──────────┼────────┼─────────────────┼────────┤   │
│    │ John   │ Acme Co  │ Open   │ $1,000,000.00  │ john@  │   │
│    │ Jane   │ Tech Inc │ Won    │ $500,000.00    │ jane@  │   │
│    └────────┴──────────┴────────┴─────────────────┴────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Key Takeaways

1. **Override happens at controller loading time** - not at runtime
2. **Frappe's hooks system** is the mechanism - it's part of the framework
3. **Your method returns metadata** (columns/rows) - not the actual data
4. **Database query uses your metadata** - to fetch the right fields
5. **Frontend receives everything** - no frontend changes needed
6. **Formatting happens in parent** - Leads.vue formats the currency
7. **Display is automatic** - LeadsListView just renders what it receives

---

## Frontend Vue.js Override

### Setup Overview

The frontend override system uses a build script that:
1. Copies original CRM source files
2. Overlays your custom files from `src_overrides/`
3. Builds the merged code with Vite
4. Outputs to your custom app

### Configuration Files

#### 1. Custom Build Script

**File**: `frontend/custom-build.mjs`

```javascript
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const crmAppPath = path.resolve(__dirname, '../../crm/frontend');
const overrideSrcPath = path.resolve(__dirname, 'src');
const overrideFilesPath = path.resolve(__dirname, './src_overrides');

console.log('Starting: Copying original src from CRM app.');
fs.copySync(path.join(crmAppPath, 'src'), overrideSrcPath);
console.log('Completed: Copying original src.');

console.log('Starting: Overriding src with custom files.');
fs.copySync(overrideFilesPath, overrideSrcPath);
console.log('Completed: Overriding src.');

console.log('Installing dependencies...');
execSync('yarn install', { stdio: 'inherit' });
console.log('Dependencies installed.');
```

#### 2. Package.json Scripts

**File**: `frontend/package.json`

```json
{
  "scripts": {
    "prebuild": "node ./custom-build.mjs",
    "dev": "vite",
    "build": "yarn prebuild && vite build --base=/assets/crm_overrides/frontend/ && yarn copy-html-entry",
    "copy-html-entry": "cp ../crm_overrides/public/frontend/index.html ../crm_overrides/www/crm.html",
    "serve": "vite preview"
  }
}
```

#### 3. Vite Configuration

**File**: `frontend/vite.config.js`

Key changes:
```javascript
buildConfig: {
  indexHtmlPath: '../crm_overrides/www/crm.html',
  emptyOutDir: true,
  sourcemap: true,
  outDir: '../crm_overrides/public/frontend',
}
```

#### 4. Web Route Handler

**File**: `crm_overrides/www/crm.py`

```python
import frappe
from frappe.utils import cint, get_system_timezone
from frappe.integrations.frappe_providers.frappecloud_billing import is_fc_site
from frappe.utils.telemetry import capture

no_cache = 1

def get_context():
    frappe.db.commit()
    context = frappe._dict()
    context.boot = get_boot()
    if frappe.session.user != "Guest":
        capture("active_site", "crm")
    return context

def get_boot():
    return frappe._dict({
        "frappe_version": frappe.__version__,
        "default_route": get_default_route(),
        "site_name": frappe.local.site,
        "read_only_mode": frappe.flags.read_only,
        "csrf_token": frappe.sessions.get_csrf_token(),
        "setup_complete": cint(frappe.get_system_settings("setup_complete")),
        "sysdefaults": frappe.defaults.get_defaults(),
        "is_demo_site": frappe.conf.get("is_demo_site"),
        "is_fc_site": is_fc_site(),
        "timezone": {
            "system": get_system_timezone(),
            "user": frappe.db.get_value("User", frappe.session.user, "time_zone")
            or get_system_timezone(),
        },
    })

def get_default_route():
    return "/crm"
```

#### 5. Hooks Website Routes

**File**: `crm_overrides/hooks.py`

```python
# Website Route Rules
website_route_rules = [
    {"from_route": "/crm/<path:app_path>", "to_route": "crm"},
]
```

---

## Build Process

### Build Flow

```
1. Run: yarn build
   ↓
2. Execute: custom-build.mjs
   ├─> Copy: apps/crm/frontend/src → apps/crm_overrides/frontend/src
   └─> Copy: apps/crm_overrides/frontend/src_overrides → apps/crm_overrides/frontend/src
   ↓
3. Vite builds merged source
   ↓
4. Output: crm_overrides/public/frontend/
   ↓
5. Copy HTML: crm_overrides/www/crm.html
```

### Build Commands

```bash
# Navigate to frontend directory
cd apps/crm_overrides/frontend

# Development mode (hot reload)
yarn dev

# Production build
yarn build
```

### What Gets Overridden

Only files you place in `src_overrides/` will override the original CRM files. The rest of the CRM code remains unchanged.

**Example**: To override LeadsListView component:

```bash
# Copy original to override directory (maintaining structure)
cp apps/crm/frontend/src/components/ListViews/LeadsListView.vue \
   apps/crm_overrides/frontend/src_overrides/components/ListViews/

# Make your changes to the copied file
# Build
cd apps/crm_overrides/frontend
yarn build
```

---

## Usage

### Complete Workflow

1. **Make Python Changes** (if needed)
   ```bash
   # Edit: crm_overrides/overrides/crm_lead.py
   # Register in: crm_overrides/hooks.py
   bench restart
   ```

2. **Make Frontend Changes** (if needed)
   ```bash
   # Copy component to: frontend/src_overrides/
   # Make changes
   cd apps/crm_overrides/frontend
   yarn build
   bench restart
   ```

3. **Test**
   - Navigate to CRM Leads list
   - Verify Annual Revenue column appears
   - Verify any UI changes work correctly

### Development Tips

1. **Python Only**: If you only change Python, no frontend build needed
2. **Frontend Only**: If you only change Vue components, must build frontend
3. **Both**: Change both, build frontend, restart bench
4. **Hot Reload**: Use `yarn dev` for active frontend development

---

## Adding More Overrides

### Override Another DocType

**Example**: Override CRM Deal

1. Create override class:
   ```python
   # File: crm_overrides/overrides/crm_deal.py
   from crm.fcrm.doctype.crm_deal.crm_deal import CRMDeal
   
   class CustomCRMDeal(CRMDeal):
       @staticmethod
       def default_list_data():
           # Your custom columns/rows
           pass
   ```

2. Register in hooks:
   ```python
   override_doctype_class = {
       "CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead",
       "CRM Deal": "crm_overrides.overrides.crm_deal.CustomCRMDeal",
   }
   ```

### Override Another Vue Component

**Example**: Override DealsListView

1. Copy component:
   ```bash
   mkdir -p apps/crm_overrides/frontend/src_overrides/components/ListViews
   cp apps/crm/frontend/src/components/ListViews/DealsListView.vue \
      apps/crm_overrides/frontend/src_overrides/components/ListViews/
   ```

2. Make changes to the copied file

3. Build:
   ```bash
   cd apps/crm_overrides/frontend
   yarn build
   ```

### Override a Page

**Example**: Override Leads.vue page

1. Copy page:
   ```bash
   mkdir -p apps/crm_overrides/frontend/src_overrides/pages
   cp apps/crm/frontend/src/pages/Leads.vue \
      apps/crm_overrides/frontend/src_overrides/pages/
   ```

2. Customize as needed

3. Build and restart

---

## Data Flow Diagram

### Backend to Frontend

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend (ViewControls.vue)                              │
│    └─> API Call: crm.api.doc.get_data                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 2. Backend (Python)                                          │
│    ├─> Frappe checks override_doctype_class                 │
│    ├─> Loads: CustomCRMLead (not CRMLead)                   │
│    ├─> Calls: CustomCRMLead.default_list_data()             │
│    │   └─> Returns: columns (with annual_revenue)           │
│    │   └─> Returns: rows (field names to fetch)             │
│    └─> Fetches data from database                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 3. Response to Frontend                                      │
│    {                                                         │
│      data: [...],           // Lead records                  │
│      columns: [...],        // Including annual_revenue      │
│      rows: [...],           // Field names                   │
│      page_length: 20,                                        │
│      total_count: 100                                        │
│    }                                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 4. Leads.vue (Parent Component)                             │
│    ├─> Receives: leads.data                                 │
│    ├─> Computes: rows (processes data)                      │
│    └─> Passes to LeadsListView:                             │
│        • :columns="leads.data.columns"                       │
│        • :rows="rows"                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 5. LeadsListView.vue (Display Component)                    │
│    └─> Renders table with all columns including             │
│        Annual Revenue                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Benefits

### 1. **Separation of Concerns**
- Core CRM code remains untouched
- All customizations in one place
- Easy to enable/disable overrides

### 2. **Upgrade Safety**
- Update core CRM without losing customizations
- Only merge conflicts in files you've overridden
- Clear upgrade path

### 3. **Maintainability**
- Clear structure for customizations
- Easy to track what's been modified
- Team-friendly approach

### 4. **Flexibility**
- Override only what you need
- Mix Python and Vue.js overrides
- Progressive enhancement approach

---

## Troubleshooting

### Python Override Not Working

1. Check hooks registration:
   ```python
   # In crm_overrides/hooks.py
   override_doctype_class = {
       "CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead",
   }
   ```

2. Verify class inheritance:
   ```python
   class CustomCRMLead(CRMLead):  # Must inherit from CRMLead
       pass
   ```

3. Restart bench:
   ```bash
   bench restart
   ```

4. Check logs:
   ```bash
   bench --verbose
   ```

### Frontend Build Issues

1. Clear node_modules:
   ```bash
   cd apps/crm_overrides/frontend
   rm -rf node_modules yarn.lock
   yarn install
   ```

2. Check Vite config paths:
   - `outDir` points to `../crm_overrides/public/frontend`
   - `indexHtmlPath` points to `../crm_overrides/www/crm.html`

3. Verify src_overrides structure matches original:
   ```bash
   # Original: apps/crm/frontend/src/components/ListViews/LeadsListView.vue
   # Override: apps/crm_overrides/frontend/src_overrides/components/ListViews/LeadsListView.vue
   ```

### Changes Not Appearing

1. Clear browser cache (Ctrl+Shift+R)
2. Check if override app is installed:
   ```bash
   bench list-apps
   ```
3. Verify file permissions
4. Check bench logs for errors

---

## How Frappe Handles Multiple Hooks (App Priority)

### The Question
You have two hooks files:
1. `apps/crm/crm/hooks.py` - Contains `override_doctype_class` for Contact and Email Template
2. `apps/crm_overrides/crm_overrides/hooks.py` - Contains `override_doctype_class` for CRM Lead

**How does Frappe know which one to use?**

### Answer: App Installation Order + Hook Merging

#### Step 1: Apps Are Loaded in Installation Order

**File**: `sites/[sitename]/apps.txt`

```
frappe
crm
crm_overrides
```

This file determines the order in which apps are loaded. You can check this with:
```bash
bench list-apps
# or
cat sites/[sitename]/apps.txt
```

#### Step 2: Frappe Merges All Hooks

**Location**: `apps/frappe/frappe/__init__.py` (lines 942-965)

```python
def _load_app_hooks(app_name: str | None = None):
    import types
    
    hooks = {}
    # Load apps in order from apps.txt
    apps = [app_name] if app_name else get_installed_apps(_ensure_on_bench=True)
    
    # Loop through each app in order
    for app in apps:  # frappe → crm → crm_overrides
        try:
            app_hooks = get_module(f"{app}.hooks")  # Import app's hooks.py
        except ImportError as e:
            print(f'Could not find app "{app}": \n{e}')
            raise
        
        def _is_valid_hook(obj):
            return not isinstance(obj, types.ModuleType | types.FunctionType | type)
        
        # Get all hook variables from the module
        for key, value in inspect.getmembers(app_hooks, predicate=_is_valid_hook):
            if not key.startswith("_"):
                # IMPORTANT: append_hook MERGES, not replaces!
                append_hook(hooks, key, value)
    
    return hooks
```

#### Step 3: Hook Merging Logic

**Location**: `apps/frappe/frappe/__init__.py` (lines 997-1015)

```python
def append_hook(target, key, value):
    """appends a hook to the target dict.
    
    If the hook key exists, it will make it a list.
    If the hook value is a dict, like doc_events, it will
    listify the values against the key.
    """
    if isinstance(value, dict):
        # For dict hooks like override_doctype_class
        target.setdefault(key, {})
        for inkey in value:
            append_hook(target[key], inkey, value[inkey])
    else:
        # For list hooks like doc_events
        target.setdefault(key, [])
        if not isinstance(value, list):
            value = [value]
        target[key].extend(value)  # EXTEND, not replace!
```

#### Step 4: What Actually Happens

Let's trace through your setup:

**1. Load frappe hooks** (no override_doctype_class)
```python
hooks = {}
```

**2. Load crm hooks** (`apps/crm/crm/hooks.py`)
```python
override_doctype_class = {
    "Contact": "crm.overrides.contact.CustomContact",
    "Email Template": "crm.overrides.email_template.CustomEmailTemplate",
}

# After merging:
hooks = {
    'override_doctype_class': {
        'Contact': ['crm.overrides.contact.CustomContact'],
        'Email Template': ['crm.overrides.email_template.CustomEmailTemplate']
    }
}
```

**3. Load crm_overrides hooks** (`apps/crm_overrides/crm_overrides/hooks.py`)
```python
override_doctype_class = {
    "CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead",
}

# After merging (ADDS to existing dict, doesn't replace!):
hooks = {
    'override_doctype_class': {
        'Contact': ['crm.overrides.contact.CustomContact'],
        'Email Template': ['crm.overrides.email_template.CustomEmailTemplate'],
        'CRM Lead': ['crm_overrides.overrides.crm_lead.CustomCRMLead']  # ← ADDED
    }
}
```

#### Step 5: Using the Merged Hooks

**Location**: `apps/frappe/frappe/model/base_document.py` (line 111)

```python
def import_controller(doctype):
    # ... original class loading ...
    
    # Get ALL overrides from ALL apps
    class_overrides = frappe.get_hooks("override_doctype_class")
    # Returns: {
    #   'Contact': ['crm.overrides.contact.CustomContact'],
    #   'Email Template': ['crm.overrides.email_template.CustomEmailTemplate'],
    #   'CRM Lead': ['crm_overrides.overrides.crm_lead.CustomCRMLead']
    # }
    
    if class_overrides and class_overrides.get(doctype):
        # For 'CRM Lead', gets: ['crm_overrides.overrides.crm_lead.CustomCRMLead']
        import_path = class_overrides[doctype][-1]  # ← Takes LAST item if multiple
        
        # Load your custom class
        module_path, custom_classname = import_path.rsplit(".", 1)
        custom_module = frappe.get_module(module_path)
        custom_class_ = getattr(custom_module, custom_classname, None)
        
        # Use it!
        class_ = custom_class_
    
    return class_
```

### Key Points

1. **Hooks are MERGED, not replaced**
   - Each app's hooks are added to a combined dictionary
   - Dict-based hooks (like `override_doctype_class`) merge their keys
   - List-based hooks (like `doc_events`) extend the list

2. **App order matters for CONFLICTS**
   - If two apps override the SAME doctype:
   ```python
   # CRM hooks
   override_doctype_class = {"CRM Lead": "crm.overrides.CustomLead"}
   
   # Your override
   override_doctype_class = {"CRM Lead": "crm_overrides.overrides.CustomCRMLead"}
   
   # Result:
   {
       'CRM Lead': [
           'crm.overrides.CustomLead',           # From CRM (loaded first)
           'crm_overrides.overrides.CustomCRMLead'  # From crm_overrides (loaded second)
       ]
   }
   
   # Frappe uses: class_overrides[doctype][-1]  ← LAST ONE WINS!
   # So: crm_overrides.overrides.CustomCRMLead is used
   ```

3. **Later apps override earlier apps**
   - The `[-1]` in `class_overrides[doctype][-1]` means "take the last one"
   - Since `crm_overrides` loads after `crm`, your override wins
   - This is intentional design for customization!

4. **Multiple apps can override different doctypes**
   - CRM overrides: Contact, Email Template
   - Your app overrides: CRM Lead
   - No conflict! All work together

### Practical Example

```python
# apps.txt order:
# 1. frappe
# 2. crm
# 3. crm_overrides
# 4. erpnext (hypothetically)

# If all had overrides for CRM Lead:
override_doctype_class = {
    'CRM Lead': [
        'crm.overrides.CRMLead',              # Position 0 (from crm)
        'crm_overrides.overrides.CustomCRMLead',  # Position 1 (from crm_overrides)
        'erpnext.overrides.ERPNextLead'           # Position 2 (from erpnext)
    ]
}

# Frappe uses: class_overrides['CRM Lead'][-1]
# Result: ERPNextLead (last app wins!)
```

### Viewing Merged Hooks

You can inspect merged hooks in bench console:

```python
# Start bench console
bench console

# Check all hooks
frappe.get_hooks()

# Check specific hook
frappe.get_hooks('override_doctype_class')
# Returns: {'Contact': [...], 'Email Template': [...], 'CRM Lead': [...]}

# Check for specific doctype
frappe.get_hooks('override_doctype_class').get('CRM Lead')
# Returns: ['crm_overrides.overrides.crm_lead.CustomCRMLead']
```

### Best Practices

1. **Don't override the same doctype in multiple custom apps**
   - Only one will win (the last one)
   - Can cause confusion

2. **Name your custom app appropriately**
   - Install it AFTER the app you're overriding
   - Use meaningful names like `crm_overrides` or `crm_extensions`

3. **Document your overrides**
   - List what you're overriding in README
   - Makes team collaboration easier

4. **Check for conflicts**
   ```python
   # In bench console
   frappe.get_hooks('override_doctype_class').get('CRM Lead')
   # If this returns a LIST with multiple items, you have a conflict!
   ```

---

## References

- **Frappe Framework**: https://frappeframework.com/docs
- **Frappe CRM**: https://github.com/frappe/crm
- **Override Guide**: https://discuss.frappe.io/t/overriding-frappe-ui-a-step-by-step-guide-with-explanations/139522
- **Vue.js**: https://vuejs.org/
- **Vite**: https://vitejs.dev/

---

## Summary

This override system provides a clean, maintainable way to customize Frappe CRM:

1. **Python overrides** handle backend logic and data structure
2. **Vue.js overrides** handle frontend UI and behavior
3. **Build system** automatically merges your changes with core CRM
4. **Modular approach** keeps customizations separate and upgrade-safe

Start with Python overrides (easier, no build required), then add frontend overrides when you need UI customization.

---

**Last Updated**: March 2025  
**Maintained By**: CRM Overrides Team

