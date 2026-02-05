# Screenshot Guide

## Required Screenshots

### 1. Telegram Bot Interface (3 screenshots)

**A. Welcome Screen (`telegram-welcome.png`)**
- Take screenshot of `/start` command response
- Should show welcome message and available commands
- Include bot's inline keyboard if present

**B. Login Process (`telegram-login.png`)**
- Show user entering phone number
- Bot requesting verification code
- Authentication flow

**C. Search & Results (`telegram-search.png`)**
- Show user initiating search with `/search`
- Chat selection prompt
- Keywords entry
- Date range inputs
- Results with clickable message links

### 2. Desktop GUI (4 screenshots)

**A. Login Window (`gui-login.png`)**
- Initial login screen
- Phone number entry field
- Verification code input
- 2FA password field (if applicable)

**B. Main Window (`gui-main.png`)**
- Full application window after login
- Chat selection dropdown
- Keywords input field
- Date range selectors
- Search button
- Empty results panel

**C. Search Results (`gui-results.png`)**
- Results list populated with messages
- Message preview text
- Chat names
- Clickable message links
- Scrollable results area

**D. Session Management (`gui-session.png`)**
- Logout button visible
- Session status indicator
- User information display

## How to Take Screenshots

### For Telegram Bot:

1. **Start the bot:**
   ```bash
   python run_bot.py
   ```

2. **Open Telegram** and find your bot

3. **Capture screenshots for each command:**
   - `/start` - Welcome screen
   - `/login` - Authentication process
   - `/search` - Complete search flow with results

4. **Taking screenshots:**
   - **Mobile:** Volume Down + Power (Android) or Side Button + Volume Up (iPhone)
   - **Desktop Telegram:** 
     - Windows: Win + Shift + S or Snipping Tool
     - Mac: Cmd + Shift + 4
     - Linux: Screenshot app or `gnome-screenshot`

### For Desktop GUI:

1. **Start the application:**
   ```bash
   python run_gui.py
   ```

2. **Navigate through different screens:**
   - Login screen
   - Main search interface
   - Results view
   - Settings/session management

3. **Capture screenshots:**
   - **Windows:** Win + Shift + S (Snipping Tool)
   - **Mac:** Cmd + Shift + 4 (then select area)
   - **Linux:** 
     - `gnome-screenshot -a` (area selection)
     - `flameshot gui` (if installed)
     - Built-in screenshot tool

## Screenshot Specifications

### Dimensions
- **Telegram Mobile:** 1080x1920 (portrait) or 720x1280
- **Telegram Desktop:** 1200x800 or 1400x900
- **GUI Application:** 1400x900 minimum (or application's natural size)

### Format
- **File format:** PNG (preferred for UI screenshots)
- **Color depth:** 24-bit or 32-bit with transparency
- **Compression:** Use lossless compression

### Quality Guidelines
- **Resolution:** High DPI/Retina if possible
- **Clarity:** Sharp text, no blur
- **Lighting:** Good contrast, readable text
- **Framing:** Include relevant UI elements, minimal extra space

## File Naming Convention

Save screenshots in `docs/screenshots/` directory:

```
docs/screenshots/
├── telegram-welcome.png
├── telegram-login.png
├── telegram-search.png
├── gui-login.png
├── gui-main.png
├── gui-results.png
└── gui-session.png
```

## Editing Screenshots

### Privacy & Security
1. **Blur sensitive information:**
   - Phone numbers
   - API keys/tokens
   - Personal chat content
   - User names (if desired)
   - Profile pictures

2. **Tools for editing:**
   - **Online:** [Photopea](https://www.photopea.com/) (free Photoshop alternative)
   - **Windows:** Paint, Paint 3D, or GIMP
   - **Mac:** Preview, Pixelmator, or GIMP
   - **Linux:** GIMP, Krita, or ImageMagick

### Annotations (Optional)
- Add arrows to highlight important features
- Add numbered callouts for step-by-step guides
- Add text labels for clarity
- Use consistent color scheme (project brand colors)

### Optimization
1. **Compress images:**
   - Online: [TinyPNG](https://tinypng.com/)
   - Command line: `pngquant` or `optipng`
   
   ```bash
   # Using optipng
   optipng -o7 *.png
   
   # Using pngquant
   pngquant --quality=80-90 *.png
   ```

2. **Target file sizes:**
   - Individual screenshots: < 500KB each
   - Total for all screenshots: < 3MB

## Example Screenshot Workflow

### Telegram Bot Screenshots

```bash
# 1. Start bot
python run_bot.py

# 2. Open Telegram, interact with bot
# 3. Take screenshots after each command
# 4. Save to docs/screenshots/

# 5. Rename and organize
mv ~/Screenshots/IMG_001.png docs/screenshots/telegram-welcome.png
mv ~/Screenshots/IMG_002.png docs/screenshots/telegram-login.png
mv ~/Screenshots/IMG_003.png docs/screenshots/telegram-search.png
```

### Desktop GUI Screenshots

```bash
# 1. Start GUI
python run_gui.py

# 2. Take screenshots of each screen
# 3. Save to docs/screenshots/

# 4. Rename and organize
mv ~/Screenshots/screenshot_001.png docs/screenshots/gui-login.png
mv ~/Screenshots/screenshot_002.png docs/screenshots/gui-main.png
mv ~/Screenshots/screenshot_003.png docs/screenshots/gui-results.png
mv ~/Screenshots/screenshot_004.png docs/screenshots/gui-session.png
```

## Updating Screenshots

When updating screenshots after code changes:

1. **Delete old screenshots** from `docs/screenshots/`
2. **Follow the capture process** above
3. **Verify all links** in README.md still work
4. **Commit changes:**
   ```bash
   git add docs/screenshots/
   git commit -m "docs: update application screenshots"
   git push
   ```

## Using Screenshots in Documentation

### In README.md

```markdown
### Main Window
![Main Window](docs/screenshots/gui-main.png)
*Main interface with login and search functionality*
```

### In Other Documentation

```markdown
## Bot Interface

The Telegram bot provides a conversational interface:

![Bot Welcome Screen](docs/screenshots/telegram-welcome.png)

After starting the bot with `/start`, you'll see available commands.
```

## Best Practices

### Do's ✅
- Use consistent window sizes
- Take screenshots in light mode (better readability in docs)
- Include relevant context in frame
- Use high-quality displays
- Test image links after adding to docs

### Don'ts ❌
- Don't include personal/sensitive information
- Don't use blurry or low-resolution images
- Don't crop important UI elements
- Don't use inconsistent image sizes
- Don't forget to compress large images

## Troubleshooting

**Issue:** Screenshots too large
- **Solution:** Use PNG optimization tools or convert to JPEG for photos

**Issue:** Text not readable
- **Solution:** Use higher resolution display or zoom in before capturing

**Issue:** Broken image links in README
- **Solution:** Verify file paths are correct and files exist in `docs/screenshots/`

**Issue:** Dark mode screenshots hard to see on light backgrounds
- **Solution:** Add border or use light mode for documentation screenshots

## Quick Reference

```bash
# Create screenshots directory
mkdir -p docs/screenshots

# Optimize all PNG files
optipng -o7 docs/screenshots/*.png

# Check file sizes
du -h docs/screenshots/*

# Compress with pngquant
pngquant --quality=80-90 docs/screenshots/*.png

# Bulk rename (if needed)
cd docs/screenshots
for f in *.png; do echo "$f -> ${f// /-}"; mv "$f" "${f// /-}"; done
```

---

**Note:** Screenshots are optional but highly recommended for better documentation. If you need help taking or editing screenshots, feel free to ask!
