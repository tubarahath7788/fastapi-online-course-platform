# 🚀 Online Course Platform (FastAPI Project)

## 📌 Project Description
This is a FastAPI backend project for an Online Course Platform.
It allows users to browse courses, enroll, manage cart, and perform advanced operations like search, sorting, and pagination.

---

## ⚙️ Features

- REST APIs using FastAPI
- Pydantic data validation
- CRUD operations
- Enrollment system
- Cart & Checkout workflow
- Search functionality
- Sorting
- Pagination
- Combined browsing API

---

## 📡 API Endpoints

### Basic APIs
- GET /
- GET /courses
- GET /courses/{id}
- GET /courses/summary

### Enrollment
- POST /enroll
- GET /enrollments

### Filtering
- GET /courses/filter

### CRUD
- POST /courses
- PUT /courses/{id}
- DELETE /courses/{id}

### Cart Workflow
- POST /cart/add
- GET /cart
- POST /cart/checkout

### Advanced APIs
- GET /courses/search
- GET /courses/sort
- GET /courses/page
- GET /courses/browse
- GET /enrollments/search
- GET /enrollments/sort

---

## ▶️ How to Run

1. Install dependencies:
pip install fastapi uvicorn

2. Run server:
uvicorn main:app --reload

3. Open Swagger UI:
http://127.0.0.1:8000/docs

---

## 📸 Screenshots

All API screenshots are available in the `screenshots` folder.

---

## 🙌 Acknowledgement

This project was built as part of FastAPI Internship Training.