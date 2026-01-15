# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-15

### Security
- **CRITICAL**: Updated all dependencies to address security vulnerabilities
- Updated `fastapi` from 0.104.1 to 0.115.0 (fixes Content-Type Header ReDoS)
- Updated `python-multipart` from 0.0.6 to 0.0.18 (fixes DoS vulnerabilities)
- Updated `Pillow` from 10.1.0 to 11.1.0 (fixes buffer overflow)
- Updated `protobuf` from 3.20.3 to 5.29.5 (fixes multiple DoS vulnerabilities)
- Updated `torch` from 2.1.1 to 2.6.0 (fixes heap overflow, use-after-free, RCE)
- Updated `transformers` from 4.35.2 to 4.48.0 (fixes deserialization vulnerabilities)
- Updated `pydantic` from 2.5.0 to 2.10.6
- Updated `uvicorn` from 0.24.0 to 0.34.0
- Updated `python-docx` from 1.1.0 to 1.1.2
- Updated `pdfplumber` from 0.10.3 to 0.11.4
- Updated `reportlab` from 4.0.7 to 4.2.5
- Updated `numpy` from 1.26.2 to 2.2.2
- Updated `httpx` from 0.25.2 to 0.28.1
- Added SECURITY.md with security policy and best practices

### Documentation
- Added security badges to README.md
- Added CHANGELOG.md to track version changes
- Updated documentation to reference security updates

## [1.0.0] - 2025-01-15

### Added
- Initial release of AI Text Spotter
- Three-detector ensemble architecture:
  - Mathematical/Statistical detector (6 features)
  - LLM detector (DistilBERT-based)
  - Jury detector (Groq Llama 3.1 8B)
- Sentence-level text analysis
- Color-coded highlighting (Green/Yellow/Red)
- File upload support (PDF, DOCX, TXT)
- Export functionality (DOCX, PDF with highlights)
- FastAPI backend with comprehensive API
- Vanilla JavaScript frontend (no frameworks)
- Docker deployment configuration
- Complete documentation:
  - README.md (comprehensive guide)
  - QUICKSTART.md (rapid setup)
  - TESTING.md (testing guide)
  - CONTRIBUTING.md (contribution guidelines)
  - IMPLEMENTATION_SUMMARY.md (project overview)
- Example cover letters for testing
- Automated test suite
- Project verification script

### Features
- Real-time text analysis
- Interactive sentence details
- Responsive design
- Accessibility features (WCAG compliant)
- Memory-optimized for AWS t3.micro (1GB RAM)
- Lazy loading for ML models
- Comprehensive error handling
- API documentation (auto-generated)

### Technical
- Python 3.10+ backend
- FastAPI web framework
- Pydantic data validation
- HuggingFace Transformers
- PyTorch deep learning
- Docker containerization
- Nginx reverse proxy

---

## Version History

- **1.0.1** - Security updates (January 2025)
- **1.0.0** - Initial release (January 2025)

## Upgrade Guide

### Upgrading from 1.0.0 to 1.0.1

#### For Local Development

```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

#### For Docker Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Breaking Changes

None. This is a security-only update with no API or functionality changes.

#### Notes

- Model files are cached locally and don't need re-download
- Configuration files (.env) remain unchanged
- No database migrations needed (stateless application)

## Future Roadmap

### Planned for 1.1.0
- [ ] Batch file processing
- [ ] Enhanced statistical features
- [ ] Performance optimizations
- [ ] Additional file format support
- [ ] Improved caching

### Planned for 1.2.0
- [ ] User preferences storage
- [ ] Analysis history
- [ ] Comparison features
- [ ] Advanced visualizations
- [ ] API rate limiting

### Under Consideration
- Multi-language support
- User authentication
- Browser extension
- Mobile applications
- Advanced analytics

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Security

See [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
