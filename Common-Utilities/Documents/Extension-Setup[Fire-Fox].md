To load your Firefox extension, follow these steps:

### 1. Open Firefox

Launch the Firefox browser.

---

### 2. Open the debugging page

Click the address bar at the top (where you normally type websites).

Type:

```
about:debugging
```

Press **Enter**.

You can also type:

```
about:debugging#/runtime/this-firefox
```

This directly opens the correct page.

---

### 3. Find "This Firefox"

You will see a page called **Add-ons Manager**.

On the left side menu, click:

```
This Firefox
```

It should be under:

```
Setup
│
├── This Firefox
└── This Nightly (if you use Nightly)
```

---

### 4. Load your extension

Click:

```
Load Temporary Add-on...
```

A file picker will open.

---

### 5. Select your `manifest.json`

Navigate to your extension folder.

Example:

```
D:\projects\my-extension
│
├── manifest.json
├── background.js
├── popup.html
├── popup.js
└── styles.css
```

Select:

```
manifest.json
```

Click:

```
Open
```

---

### 6. Confirm it loaded

You should now see your extension listed under:

```
Temporary Extensions
```

You can click:

```
Inspect
```

to open developer tools for the extension.

---

### If you cannot find `about:debugging`

Make sure you are typing it in the **address bar**, not Google search.

Correct:

```
Firefox address bar → about:debugging → Enter
```

Not:

```
Google search → about:debugging
```

---

### If Firefox says "Manifest is invalid"

Check:

1. Your file is exactly named:

```
manifest.json
```

not:

```
manifest.json.txt
```

2. The file contains valid JSON.

Example minimal Firefox extension:

```json
{
  "manifest_version": 2,
  "name": "My Extension",
  "version": "1.0",
  "description": "Test extension",
  "browser_action": {
    "default_title": "My Extension"
  }
}
```

---

Once loaded, the extension only stays installed until Firefox closes. After restarting Firefox, you need to load it again (temporary extensions behave this way).
