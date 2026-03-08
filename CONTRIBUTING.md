# Contributing to SadakAI

Thank you for your interest in contributing to SadakAI!

## 🤝 How to Contribute

### Reporting Bugs

1. **Search existing issues** - Someone may have already reported the problem
2. **Create a new issue** - Use the bug report template
3. **Include details**:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Browser/OS information

### Suggesting Features

1. **Check existing proposals** - Avoid duplicates
2. **Create a feature request** - Use the feature template
3. **Explain the use case** - Why is this useful?

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Write tests** (if applicable)
5. **Commit with clear messages**:
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 📋 Pull Request Guidelines

- Follow the existing code style
- Add comments for complex logic
- Update documentation if needed
- Test your changes locally
- Keep PRs focused and atomic

## 🏗️ Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Local Development

```bash
# Clone the repo
git clone https://github.com/your-username/SadakAI.git
cd SadakAI

# Set up backend
cd api
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
cd ../dashboard
cp .env.example .env
npm install
```

### Running Tests

```bash
# Backend
cd api
pytest

# Frontend
cd dashboard
npm test
```

## 📝 Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Maximum line length: 100

### TypeScript/JavaScript

- Use ESLint
- Follow existing patterns
- Use TypeScript types
- Maximum line length: 100

### CSS/Tailwind

- Use Tailwind utility classes
- Follow BEM naming for custom CSS
- Mobile-first approach

## 🎯 Areas for Contribution

### High Priority

- [ ] Bug fixes
- [ ] Performance improvements
- [ ] Documentation improvements
- [ ] Mobile responsiveness

### Medium Priority

- [ ] New features
- [ ] Test coverage
- [ ] UI/UX improvements

### Low Priority

- [ ] New hazard types
- [ ] Advanced analytics
- [ ] User authentication

## 💬 Communication

- **GitHub Issues** - For bugs and features
- **GitHub Discussions** - For questions
- **Discord** - (if available)

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

---

**Thank you for contributing to safer Indian roads! 🛣️**
