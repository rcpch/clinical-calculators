# RCPCH Clinical Calculators - Web Client

This directory contains the static web client for RCPCH Clinical Calculators, built with DaisyUI and Tailwind CSS.

## Features

- 🎨 **RCPCH Branded Design** - Uses official RCPCH colors and styling
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- 🔄 **Dynamic Forms** - Automatically generates forms from calculator specs
- ⚡ **Fast** - Static site hosted on GitHub Pages
- ♿ **Accessible** - Built with accessibility in mind using DaisyUI components

## Files

- `index.html` - Main page with calculator list and form interface
- `app.js` - JavaScript for fetching calculators and handling form submissions
- `config.js` - API endpoint configuration
- `colors.md` - RCPCH brand color reference

## Local Development

1. **Start the API** (from project root):
   ```bash
   docker compose up
   ```

2. **Serve the docs folder**:
   ```bash
   # Option 1: Python
   cd docs
   python3 -m http.server 3000
   
   # Option 2: Node.js
   npx serve docs -p 3000
   
   # Option 3: VS Code Live Server extension
   # Right-click index.html > "Open with Live Server"
   ```

3. **Open in browser**:
   ```
   http://localhost:3000
   ```

The site will automatically connect to the API at `http://localhost:8000` when running locally.

## Deployment to GitHub Pages

1. **Enable GitHub Pages** in repository settings:
   - Go to Settings > Pages
   - Source: Deploy from a branch
   - Branch: `live` (or your default branch)
   - Folder: `/docs`
   - Save

2. **Update API URL** in `config.js`:
   ```javascript
   baseUrl: 'https://your-api-domain.com'
   ```

3. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Add web client"
   git push origin live
   ```

4. **Access the site**:
   ```
   https://rcpch.github.io/clinical-calculators/
   ```

## Customization

### Colors
All RCPCH brand colors are defined in:
- `colors.md` - Reference documentation
- `index.html` - Tailwind config section
- DaisyUI theme configuration

### API Endpoint
Update the API URL in `config.js` to point to your deployed API.

### Styling
The site uses DaisyUI components with a custom RCPCH theme. Modify the `daisyui.themes` object in `index.html` to adjust colors.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

To add new features or fix bugs:

1. Test locally with the development API
2. Commit changes to a feature branch
3. Create a pull request to `live` branch
4. After merge, changes will automatically deploy to GitHub Pages

## License

Copyright © 2025 Royal College of Paediatrics and Child Health
