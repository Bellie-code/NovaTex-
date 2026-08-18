# NovaTex Privacy-Aware Face Recognition Attendance System

A privacy-aware, AI-powered attendance management system combining face recognition, real-time anti-spoofing verification, automated attendance logging, and a modular web architecture.

## Overview

NovaTex Attendance System is a full-stack attendance platform built around three major layers:

- **Frontend** — React + Vite interface for administrators and employees
- **Backend** — FastAPI application for authentication, attendance, employee management, APIs, and business logic
- **AI Service** — Dedicated InsightFace-based service for face embedding generation and recognition

Supporting infrastructure includes PostgreSQL for persistent data storage, Redis for caching, and Docker Compose for containerized deployment.

The architecture separates AI processing from the main backend so face-recognition operations run through a dedicated service.

## Key Features

### Authentication
- Administrator authentication
- Employee authentication
- JWT-based authentication
- Role-based access control

### Employee Management
- Create employee accounts
- View employee information
- Face enrollment
- Face update workflow
- Face enrollment status tracking

### Face Recognition
- Camera-based face capture
- Base64 image processing
- Face embedding generation
- InsightFace-based recognition
- Dedicated AI recognition service

### Anti-Spoofing
- Challenge-based verification
- Real-time verification workflow
- Spoof detection before attendance confirmation

### Attendance
- Face-based attendance marking
- Duplicate attendance prevention
- Attendance records
- Attendance log retrieval

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| AI | InsightFace, ArcFace, ONNX Runtime, OpenCV |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT |
| Deployment | Docker, Docker Compose |

## System Architecture

React / Vite Frontend ? FastAPI Backend ? AI Face Service ? InsightFace
                                      ?
                                  PostgreSQL
                                      ?
                                    Redis

## Application Workflow

Employee Login ? Face Capture ? AI Face Service ? Identity Verification ? Anti-Spoof Verification ? Attendance Validation ? Attendance Record

## API Services

Backend: http://localhost:8000
Backend Swagger: http://localhost:8000/docs
Backend Health: http://localhost:8000/health
AI Service: http://localhost:9000
AI Service Swagger: http://localhost:9000/docs

## Running with Docker

docker compose build
docker compose up -d
docker compose ps

## Application URLs

Frontend: http://localhost:5173
Backend: http://localhost:8000
AI Service: http://localhost:9000

## Project Status

Prototype / Development Stage

The current system demonstrates an end-to-end AI-powered attendance workflow using a dedicated face-recognition service, anti-spoofing verification, database persistence, and containerized deployment.

## License

This project is currently intended for educational, research, and prototype development purposes.
