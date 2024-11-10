# Changelog

## [1.1.0] - 2024-03-10

### Added
- Multi-browser support (Chromium, Firefox, WebKit)
- Automatic browser installation
- `--browser` option to select browser engine
- Enhanced logging system with verbose and trace modes
- Browser console and network error logging
- Automatic fallback to Chromium when other browsers fail

### Changed
- Switched from Selenium to Playwright for better browser automation
- Improved proxy handling and configuration
- Enhanced error handling and recovery
- Updated proxy support (HTTP/HTTPS with auth, SOCKS5 without auth)
- Better progress reporting and debug information

### Fixed
- Image duplication in multi-image posts
- Double logging issues
- Browser installation and initialization issues
- Proxy authentication handling

### Removed
- Selenium dependencies
- Manual browser installation requirement
- SOCKS5 proxy authentication support

## [1.0.0] - Initial Release

- Initial release with basic YouTube community post scraping functionality
- Firefox/Selenium-based scraping
- Basic proxy support
- Image and comment collection
- Progress saving 