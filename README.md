# ⚠️ Repository Status

This repository is no longer actively maintained.

Its original purpose was to provide up-to-date native **RPM** and **DEB** packages for ZapZap during a period when official packages were unavailable or lagging behind the upstream project.

Fortunately, this is no longer necessary.

The upstream project once again provides official packages for both Fedora (via COPR) and Debian-based distributions, making this repository obsolete for its original purpose.

Because of that, this repository has been archived as a historical reference.

The build scripts and packaging files will remain available in case they are useful in the future, but no new releases are planned.

## Why was this repository archived?

I wrote a short article explaining the motivation behind this project, the packaging process, and why I believe archiving it is the right decision now.

📖 **When a Fork Is No Longer Needed / Cuando un fork deja de ser necesario**

https://katherineflores.me/2026/08/03/when-a-fork-is-no-longer-needed-cuando-un-fork-deja-de-ser-necesario/

The article is available in both **English** and **Spanish**.

## Recommendation

Please use the official packages provided by the upstream project whenever possible.

Thank you to everyone who downloaded, tested, reported issues, and helped improve these builds. ❤️



# [ZapZap](https://rtosta.com/zapzap-web/) – WhatsApp Desktop for Linux & Windows
![ZapZap for WhatsApp](share/screenshot/default.png)

## 📌 About

ZapZap brings the WhatsApp experience on Linux closer to that of a native application.  
Since Meta does not provide a public API for third-party applications, ZapZap is developed as a [Progressive Web Application (PWA)](https://en.wikipedia.org/wiki/Progressive_web_app), built with **PyQt6 + PyQt6-WebEngine**.

📌 Technical documentation:
See [docs/technical-documentation.md](docs/technical-documentation.md)

---

## Fork scope and support policy

This repository (`clairerb6/zapzap`) exists to keep **native Linux packaging** up to date, especially:

- RPM
- DEB

The original project direction has prioritized **Flatpak** and **AppImage**.
This fork does not redefine product direction and does not propose feature changes upstream by default.

### Where to open issues

- **New features / behavior changes**: open issues in the original repository  
  `rafatosta/zapzap`
- **Packaging and native install issues (RPM/DEB)**: open issues in this repository  
  `clairerb6/zapzap`

In short:

- New feature requests -> `rafatosta/zapzap`
- Packaging maintenance -> `clairerb6/zapzap`

---

## Alcance del fork y política de soporte (Español)

Este repositorio (`clairerb6/zapzap`) existe para mantener al día el **empaquetado nativo en Linux**, especialmente:

- RPM
- DEB

La dirección del proyecto original ha priorizado **Flatpak** y **AppImage**.
Este fork no redefine esa dirección del producto y, por defecto, no impulsa cambios de funcionalidades al upstream.

### Dónde abrir issues

- **Nuevas funcionalidades / cambios de comportamiento**: abrir issues en el repositorio original  
  `rafatosta/zapzap`
- **Problemas de empaquetado e instalación nativa (RPM/DEB)**: abrir issues en este repositorio  
  `clairerb6/zapzap`

En resumen:

- Solicitudes de nuevas características -> `rafatosta/zapzap`
- Mantenimiento de empaquetados -> `clairerb6/zapzap`

---

## 📥 Download

- **[Flathub](https://flathub.org/apps/details/com.rtosta.zapzap)**  
- **[AppImage](https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage)**

---

## ✨ Features

ZapZap extends WhatsApp Web with additional features:

### 🎨 Appearance
- Adaptive **light and dark mode**
- **Fullscreen mode**
- Custom **window decorations**
- **Interface scaling adjustment** (ideal for 2K/4K screens)

### ⚡ Usability
- **Keyboard shortcuts** for main options
- Adaptive **system tray icon** (notifies new messages)
- **Background process** support
- **Drag-and-drop** functionality
- **Account Grid View** (Quickly switch between all accounts)
- Ability to select a **custom folder for downloads**
- **Temporary folder** for opening files

### 🛠️ Extras
- **Spellchecker** with language selection via context menu
- Customizable **system tray icons**
- Option to choose a **folder for custom dictionaries**
- Setting to **disable the native file selection dialog** (Hyprland)
- **Custom CSS/JS** with global + per-account override
- **Reorganized Settings Panel**
- Added **Performance section**
- **Native Windows support** (SQLite + Registry settings)

### 🧩 Customizations
- New **Customizations** page in Settings
- Supports **Global** customization and **Current account** customization
- Account mode supports **inherit global settings** + optional override
- Users can:
  - import `.css` and `.js` files
  - create and edit CSS/JavaScript files in dialogs
  - enable/disable each imported CSS/JS file independently
  - import CSS/JavaScript from any `https://` URL
  - open customization folders directly
- Supports many userstyle files (`.user.css`) by extracting WhatsApp-targeted `@-moz-document` blocks
- Page actions: `Save`, `Save and reload`, `Reload`

Customization files are stored in the app local data path under:
- `customizations/global/css`
- `customizations/global/js`
- `customizations/accounts/<id>/css`
- `customizations/accounts/<id>/js`

Reserved for future extension support:
- `customizations/extensions`

---

## ⚠️ File upload notice

### File uploads and filesystem permissions

To enable **file uploads (documents, images, videos, audio, etc.)** in WhatsApp Web, **ZapZap requires access to the user’s folders**.

This is due to **technical limitations of QtWebEngine (Chromium)** in modern environments such as **Wayland** and **sandboxed applications** (for example, Flatpak).  
Under these conditions, the embedded browser **cannot upload files correctly** without direct access to the filesystem.

### What this means in practice

- Without filesystem access:
  - file uploads may fail
  - files may be sent **with no content**
- With the required permissions granted:
  - file uploads work correctly
  - the experience matches that of a regular web browser

### Recommended permissions

When running in a sandboxed environment (such as Flatpak), it is recommended to grant access to at least:

- `Documents`
- `Videos`
- `Pictures`
- `Downloads`

These permissions are used **only** to allow the user to select and upload files and are **not** used for automatic file scanning, indexing, or data collection.

### Changing permissions on Flatpak

If ZapZap was installed via **Flatpak**, you can manage filesystem permissions using **Flatseal** (a graphical permission manager for Flatpak apps):

👉 https://flathub.org/apps/com.github.tchx84.Flatseal

Steps:
1. Install and open **Flatseal**
2. Select **ZapZap** from the application list
3. Enable access to the recommended folders (`Documents`, `Videos`, `Pictures`, `Downloads`)
4. Restart ZapZap

Optional terminal alternative:

```bash
flatpak override --user --filesystem=home com.rtosta.zapzap
```

After adjusting these permissions, file uploads, opening PDFs, and drag-and-drop should work normally.


# ⚙️ Development

## Requirements

- **Python 3.8 or higher**
- `pip`
- System libraries required by Qt WebEngine and optionally `dbus-python` on Linux



## Fedora 43 System Dependencies

If `pip install -r requirements.txt` fails due to `dbus-python`:

``` bash
sudo dnf install -y dbus-devel pkg-config gcc python3-devel
```

Then:

``` bash
pip install -r requirements.txt
```



# 🚀 Development Mode

``` bash
python run.py
```

#### Debugging WebEngine
- Open DevTools for current account page: `View -> Open DevTools` (`Ctrl+Shift+I`)

## 🏗️ Builders

ZapZap possui builders dedicados para cada alvo de distribuição, organizados em `builders/`:

- `builders/flatpak_builder.py`: pipeline de build e empacotamento Flatpak.
- `builders/appimage_builder.py`: geração do artefato AppImage.
- `builders/windows_builder.py`: build para Windows (EXE/ZIP).

Esses builders são acionados manualmente e independente do `run.py`, mantendo um fluxo único de automação local e release.

## 📦 Build AppImage

``` bash
python builders/appimage_builder.py --appimage <version>
```

Example:

``` bash
python builders/appimage_builder.py build --appimage 6.5
```



## 📦 Build Flatpak Onefile

``` bash
python builders/flatpak_builder.py
```

Output:

    dist/com.rtosta.zapzap.flatpak
    
### 📦 Build Windows (EXE)

``` bash
python builders/windows_builder.py
```

Output:

    dist/ZapZap.exe
    dist/ZapZap-Windows.zip


## 📦 Install as Python Module

``` bash
pip install .
```

### Uninstall

``` bash
pip uninstall zapzap
```


## 🔧 uv Tool

``` bash
uv tool install . --with-requirements requirements.txt
```

## 📦 Packaging
- **[Flatpak](https://github.com/flathub/com.rtosta.zapzap)**
- **[AppImage](_scripts/build-appimage.sh)**

## 🌍 Translation
ZapZap supports translations. If your language file is missing from the [po](/po) folder, submit a pull request or open an [issue](https://github.com/rafatosta/zapzap/issues).

## 🤝 Contributions
Contributions are welcome.

Scope for this fork:
- Packaging, build scripts, and native install stability (RPM/DEB)
- Compatibility fixes that improve runtime stability across distros

For new user-facing features, please propose them in `rafatosta/zapzap`.

## 📜 License
This project is licensed under the GPL.
See the LICENSE file for more information.

## 💖 Donations
**PayPal:** [Donate via PayPal](https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD) 

**Pix:** [Donate via Pix](https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv) 

**Ko-fi:** [Donate via Ko-fi](https://ko-fi.com/X8X2E1OLG)

## 📬 Contact
**Maintainer:** Rafael Tosta 

**Email:** [rafa.ecomp@gmail.com](mailto:rafa.ecomp@gmail.com)
