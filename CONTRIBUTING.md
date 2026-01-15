# Contributing to AI Text Spotter

Thank you for your interest in contributing to AI Text Spotter! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Vlasenko2006/ai-text-spotter/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Error messages and logs

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach
   - Any relevant examples or mockups

### Code Contributions

#### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-text-spotter.git
   cd ai-text-spotter
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

3. **Set up development environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If you add this
   ```

#### Development Guidelines

**Python Code Style**:
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

**JavaScript Code Style**:
- Use consistent indentation (2 spaces)
- Use const/let instead of var
- Add JSDoc comments for functions
- Use async/await for promises
- Handle errors appropriately

**File Organization**:
- Backend: Place files in appropriate directories (detectors, services, api, etc.)
- Frontend: Keep JavaScript modules separate and focused
- Tests: Mirror the structure of the code being tested

#### Testing

**Before submitting**:
1. Run core tests:
   ```bash
   cd backend
   python tests/test_core.py
   ```

2. Test your changes manually:
   - Start backend and frontend
   - Test affected functionality
   - Try edge cases

3. Add new tests for new features:
   - Unit tests for detectors/services
   - Integration tests for API endpoints
   - Frontend tests if applicable

#### Making Changes

**Backend Changes**:
1. Update relevant detectors/services/routes
2. Add/update type hints and docstrings
3. Update schemas if API changes
4. Add tests for new functionality
5. Update documentation

**Frontend Changes**:
1. Update HTML/CSS/JavaScript as needed
2. Test on multiple browsers
3. Ensure responsive design works
4. Check accessibility (keyboard navigation, ARIA labels)
5. Update comments and documentation

**Documentation Changes**:
1. Update README.md for major changes
2. Update QUICKSTART.md if setup changes
3. Update API documentation if endpoints change
4. Add inline code comments for complex logic

#### Commit Messages

Use clear, descriptive commit messages:

```
Good:
- "Add entropy calculation to mathematical detector"
- "Fix sentence splitting for abbreviations"
- "Update README with AWS deployment instructions"

Bad:
- "Fixed bug"
- "Update"
- "WIP"
```

Format:
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link related issues
   - Add screenshots for UI changes
   - Request review

4. **PR Checklist**:
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] Tests pass
   - [ ] No merge conflicts

5. **Review Process**:
   - Address reviewer feedback
   - Make requested changes
   - Update PR description if needed
   - Request re-review

6. **After Merge**:
   - Delete your branch
   - Update your local repository
   - Close related issues

## Development Areas

### High Priority

- **Improved Mathematical Detector**: Add more statistical features
- **Performance Optimization**: Reduce memory usage, faster inference
- **Better Error Handling**: More informative error messages
- **Testing**: Increase test coverage
- **Documentation**: More examples and tutorials

### Medium Priority

- **Additional File Formats**: Support more document types
- **Batch Processing**: Analyze multiple files at once
- **User Preferences**: Save settings, themes
- **Visualization**: Charts and graphs for analysis
- **API Rate Limiting**: Implement request throttling

### Low Priority

- **Multi-language Support**: Support for non-English text
- **Authentication**: User accounts and API keys
- **History**: Save and view past analyses
- **Comparison**: Compare multiple documents

## Project Structure

```
ai-text-spotter/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── detectors/    # Detection algorithms
│   │   ├── services/     # Business logic
│   │   ├── models/       # Data models
│   │   ├── config.py     # Configuration
│   │   └── main.py       # Application entry
│   ├── tests/            # Tests
│   └── requirements.txt  # Dependencies
├── frontend/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript modules
│   └── index.html        # Main page
├── docs/                 # Documentation (future)
└── docker-compose.yml    # Docker setup
```

## Resources

- **Python**: https://www.python.org/dev/peps/pep-0008/
- **FastAPI**: https://fastapi.tiangolo.com/
- **HuggingFace**: https://huggingface.co/docs
- **Groq API**: https://console.groq.com/docs

## Questions?

- Open a [Discussion](https://github.com/Vlasenko2006/ai-text-spotter/discussions)
- Ask in an existing issue
- Check documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI Text Spotter! 🙏
