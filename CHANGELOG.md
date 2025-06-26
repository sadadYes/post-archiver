# Changelog

## [1.2.2] - 2025-06-26

### Removed
- Removed redundant HD (high resolution) image quality option
- HD quality has been replaced by the superior source quality option
- Updated CLI validation to only accept 'src', 'sd', and 'all' quality options
- Cleaned up all HD-related code from scraper and download functions

### Changed
- Source quality ('src') is now the highest resolution option available
- Updated documentation and examples to reflect HD removal

## [1.2.1] - 2024-11-12

### Fixed
- Improved commenter icon collection reliability
- Added two-pass approach for comment scraping
- Better image loading handling for comment avatars

## [1.2.0] - 2024-03-10

### Added
- New --member-only flag to only scrape membership-only posts
- Member-only status tracking for each post
- Browser cookie integration with --browser-cookies option
- Support for getting cookies directly from Chrome, Firefox, Edge, and Opera
- Improved membership post detection
- Better cookie handling and validation

### Changed
- Posts now include 'member_only' field indicating membership status
- Restructured cookie handling to support both file and browser sources
- Improved error messages for cookie-related issues

### Fixed
- Cookie conversion issues between browser and Playwright formats
- Cookie expiration handling
- Browser cookie extraction reliability

## [1.1.1] - 2024-03-10

### Fixed
- Image quality selection now properly filters images based on the --image-quality flag
- Standard quality (sd) and high resolution (hd) options now work as intended
- Fixed duplicate image collection in multi-image posts

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