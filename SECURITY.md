# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Updates

### Latest Security Patches (January 2025)

All dependencies have been updated to address known vulnerabilities:

#### Fixed Vulnerabilities

1. **FastAPI** (0.104.1 → 0.115.0)
   - Fixed: Content-Type Header ReDoS vulnerability
   - CVE: Affects versions ≤ 0.109.0

2. **python-multipart** (0.0.6 → 0.0.18)
   - Fixed: Content-Type Header ReDoS
   - Fixed: Denial of Service via malformed multipart/form-data boundary
   - CVE: Affects versions ≤ 0.0.6

3. **Pillow** (10.1.0 → 11.1.0)
   - Fixed: Buffer overflow vulnerability
   - CVE: Affects versions < 10.3.0

4. **protobuf** (3.20.3 → 5.29.5)
   - Fixed: Multiple Denial of Service vulnerabilities
   - CVE: Affects versions < 4.25.8, 5.26.0-5.29.4, 6.30.0-6.31.0

5. **torch** (2.1.1 → 2.6.0)
   - Fixed: Heap buffer overflow vulnerability
   - Fixed: Use-after-free vulnerability
   - Fixed: Remote code execution via torch.load
   - CVE: Affects versions < 2.6.0

6. **transformers** (4.35.2 → 4.48.0)
   - Fixed: Multiple deserialization of untrusted data vulnerabilities
   - CVE: Affects versions < 4.48.0

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** open a public GitHub issue
2. Email the security team at: [security contact needed]
3. Or use GitHub's private vulnerability reporting feature

### What to Include

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies by severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Best effort

## Security Best Practices

### For Deployment

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong, unique API keys
   - Rotate credentials regularly

2. **Dependencies**
   - Keep dependencies up to date
   - Run `pip list --outdated` regularly
   - Monitor security advisories

3. **File Uploads**
   - Validate file types and sizes
   - Scan uploaded files if possible
   - Limit upload directory permissions

4. **API Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Set appropriate CORS policies
   - Use authentication for sensitive endpoints

5. **Docker Security**
   - Use official base images
   - Run as non-root user
   - Scan images for vulnerabilities
   - Keep Docker updated

### For Development

1. **Virtual Environments**
   - Always use virtual environments
   - Don't install packages globally
   - Keep dev and prod dependencies separate

2. **Code Security**
   - Validate all user inputs
   - Sanitize outputs
   - Use parameterized queries
   - Avoid eval() and exec()

3. **Secrets Management**
   - Use environment variables
   - Never hardcode secrets
   - Use secret management tools for production

## Security Checklist

Before deploying to production:

- [ ] All dependencies updated to latest secure versions
- [ ] `.env` file not committed to repository
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] File upload validation implemented
- [ ] Rate limiting configured
- [ ] Security headers set (CSP, HSTS, etc.)
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Logging configured (but no sensitive data logged)
- [ ] Docker images scanned for vulnerabilities
- [ ] Backup and recovery plan in place

## Known Limitations

1. **Groq API Key**: Store securely, never commit to repository
2. **Model Files**: Downloaded from HuggingFace, verify checksums
3. **File Processing**: PDF/DOCX parsing may have edge cases
4. **Memory Limits**: DoS possible with very large files (mitigated by size limits)

## Security Headers

The application should be deployed behind a reverse proxy (nginx) with these headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

## Compliance

This application:
- Does not store user data
- Does not use cookies for tracking
- Processes files temporarily (deleted after analysis)
- Does not transmit data to third parties (except Groq API for jury detection)

## Third-Party Services

### Groq API
- Used for: Final classification (Jury detector)
- Data sent: Sentence text, detector scores
- Data retention: Per Groq's privacy policy
- Can be disabled: Yes (falls back to voting mechanism)

### HuggingFace
- Used for: Model downloads
- Data sent: None (models cached locally)
- Data retention: N/A

## Vulnerability Disclosure Timeline

We follow responsible disclosure practices:

1. **Private Report**: Vulnerability reported privately
2. **Acknowledgment**: We confirm receipt within 48 hours
3. **Investigation**: We investigate and develop a fix
4. **Patch**: We release a patched version
5. **Disclosure**: After patch is released, we publish details
6. **Credit**: Reporter credited (if desired)

## Contact

For security concerns, please contact:
- GitHub: Open a private security advisory
- Project maintainers: Via GitHub issues (for non-security questions)

---

**Last Updated**: January 2025  
**Next Review**: April 2025
