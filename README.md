# loneliness-screening-tool
A loneliness screening and visualization tool for older adults (MSIT Capstone)

Add project README with overview, stack, and structure
# Loneliness Screening and Visualization Tool for Older Adults

An MSIT Capstone project. A web application that administers the validated
Three-Item Loneliness Scale, computes a score, visualizes the trend over time,
and raises a flag when loneliness is sustained or worsening, so that an
authorized caregiver can respond.

## Tech stack
- Frontend: React
- Backend: Flask (Python)
- Database: SQLite (repository pattern; can move to PostgreSQL later)
- CI: GitHub Actions

## Repository structure
- `src/`     source code (React frontend, Flask backend)
- `docs/`    documentation (SRS, technical report, notes)
- `design/`  design files (architecture diagram, wireframes)
- `tests/`   test code
- `.github/workflows/`  continuous integration

## Branches
- `main`        stable, demoable build
- `development` integration of new work before merging into main

## Status
Detailed design stage (Unit 3). Implementation to follow.
