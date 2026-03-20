# JVET HLS Browser

Interactive specification browser for H.266/VVC video codec high-level syntax.

## Features

- 🎯 **Interactive Syntax Navigation** - Browse 40+ syntax structures with C++ style highlighting
- 📚 **Semantic Information** - View detailed semantics for 423 parameters
- 🔗 **AI-Powered Connections** - Explore relationships between parameters
- 🌳 **Connection Trees** - Visualize parameter dependencies
- 🔍 **Smart Search** - Quick search across syntax structures
- 📱 **Responsive Design** - Works on desktop and mobile

## Demo

Visit the live demo: [https://shuaizhao.github.io/jvet-hls-browser/web/login.html](https://shuaizhao.github.io/jvet-hls-browser/web/login.html)

**Login credentials:**
- Username: `admin`
- Password: `admin_password`

## Usage

1. Navigate to the login page
2. Enter credentials (admin/admin_password)
3. Browse syntax structures from the left panel
4. Click on parameters to view semantics
5. Explore connections and related parameters

## Technology Stack

- Pure HTML/CSS/JavaScript (no frameworks)
- D3.js for connection visualizations
- Font Awesome for icons
- Claude AI for connection generation

## Local Development

Simply open `web/login.html` in a browser. No build process required.

## Data Generation

The syntax and semantics data are extracted from the H.266/VVC specification:

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate connections (requires Claude API key)
export ANTHROPIC_API_KEY="your-key"
python scripts/generate_connections_simple.py --codec vvc
```

## Project Structure

```
├── web/                   # Frontend files
│   ├── index.html        # Main application
│   ├── login.html        # Login page
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── data/vvc/             # VVC specification data
│   ├── syntax.json       # Syntax structures
│   ├── semantics.json    # Parameter semantics
│   └── connections_checkpoint.json  # Parameter connections
└── scripts/              # Data generation scripts
```

## License

This project is for educational and research purposes. The H.266/VVC specification is owned by ITU-T/ISO/IEC.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

- Specification: ITU-T H.266 | ISO/IEC 23090-3
- Developed for JVET (Joint Video Experts Team)
