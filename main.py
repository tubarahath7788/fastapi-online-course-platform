from fastapi import FastAPI, Response
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# -------------------- DATA --------------------

courses = [
    {"id": 1, "title": "Python Basics", "price": 1000, "category": "Programming", "is_available": True},
    {"id": 2, "title": "Java", "price": 1200, "category": "Programming", "is_available": True},
    {"id": 3, "title": "UI/UX Design", "price": 1500, "category": "Design", "is_available": False},
    {"id": 4, "title": "Data Science", "price": 2000, "category": "Data", "is_available": True},
    {"id": 5, "title": "Digital Marketing", "price": 800, "category": "Marketing", "is_available": True},
    {"id": 6, "title": "Excel Mastery", "price": 700, "category": "Tools", "is_available": True}
]

enrollments = []
cart = []
enrollment_counter = 1

# -------------------- MODELS --------------------

class EnrollRequest(BaseModel):
    student_name: str = Field(min_length=2)
    course_id: int = Field(gt=0)
    duration: int = Field(gt=0, le=12)
    course_type: str = "online"


class NewCourse(BaseModel):
    title: str = Field(min_length=2)
    price: int = Field(gt=0)
    category: str = Field(min_length=2)
    is_available: bool = True


class CheckoutRequest(BaseModel):
    student_name: str = Field(min_length=2)


# -------------------- HELPERS --------------------

def find_course(course_id):
    for c in courses:
        if c["id"] == course_id:
            return c
    return None


def calculate_price(price, duration, course_type):
    total = price * duration
    if course_type == "offline":
        total += 500
    return total


def filter_courses_logic(category, max_price, is_available):
    result = []
    for c in courses:
        if category is not None and c["category"].lower() != category.lower():
            continue
        if max_price is not None and c["price"] > max_price:
            continue
        if is_available is not None and c["is_available"] != is_available:
            continue
        result.append(c)
    return result


# -------------------- DAY 1 --------------------

@app.get("/")
def home():
    return {"message": "Welcome to Online Course Platform"}


@app.get("/courses")
def get_courses():
    return {"total": len(courses), "courses": courses}


# ✅ FIXED ROUTES (IMPORTANT ORDER)

@app.get("/courses/filter")
def filter_courses(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_courses_logic(category, max_price, is_available)
    return {"count": len(result), "data": result}


@app.get("/courses/summary")
def summary():
    total = len(courses)
    available = len([c for c in courses if c["is_available"]])
    unavailable = total - available
    categories = list(set([c["category"] for c in courses]))

    return {
        "total": total,
        "available": available,
        "unavailable": unavailable,
        "categories": categories
    }


@app.get("/courses/search")
def search_courses(keyword: str):
    result = [
        c for c in courses
        if keyword.lower() in c["title"].lower()
        or keyword.lower() in c["category"].lower()
    ]
    return {"total_found": len(result), "data": result}


@app.get("/courses/sort")
def sort_courses(sort_by: str = "price", order: str = "asc"):
    data = sorted(courses, key=lambda x: x[sort_by])
    if order == "desc":
        data.reverse()
    return {"data": data}


@app.get("/courses/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    data = courses[start:start + limit]
    total_pages = math.ceil(len(courses) / limit)

    return {
        "page": page,
        "total_pages": total_pages,
        "data": data
    }


@app.get("/courses/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    data = courses

    # filter
    if keyword:
        data = [
            c for c in data
            if keyword.lower() in c["title"].lower()
            or keyword.lower() in c["category"].lower()
        ]

    # sort
    data = sorted(data, key=lambda x: x[sort_by])
    if order == "desc":
        data.reverse()

    # pagination
    start = (page - 1) * limit
    paginated = data[start:start + limit]

    return {
        "page": page,
        "total": len(data),
        "data": paginated
    }


# ❗ VARIABLE ROUTE LAST

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = find_course(course_id)
    if not course:
        return {"error": "Course not found"}
    return course


@app.get("/enrollments")
def get_enrollments():
    return {"total": len(enrollments), "data": enrollments}


# -------------------- DAY 2 + 3 --------------------

@app.post("/enroll")
def enroll(data: EnrollRequest):
    global enrollment_counter

    course = find_course(data.course_id)
    if not course:
        return {"error": "Course not found"}

    if not course["is_available"]:
        return {"error": "Course not available"}

    total = calculate_price(course["price"], data.duration, data.course_type)

    record = {
        "id": enrollment_counter,
        "student_name": data.student_name,
        "course": course["title"],
        "duration": data.duration,
        "course_type": data.course_type,
        "total_price": total
    }

    enrollments.append(record)
    enrollment_counter += 1

    return record


# -------------------- CRUD --------------------

@app.post("/courses")
def add_course(course: NewCourse, response: Response):
    new = course.dict()
    new["id"] = len(courses) + 1
    courses.append(new)
    response.status_code = 201
    return new


@app.put("/courses/{course_id}")
def update_course(course_id: int, price: Optional[int] = None, is_available: Optional[bool] = None):
    course = find_course(course_id)
    if not course:
        return {"error": "Course not found"}

    if price is not None:
        course["price"] = price

    if is_available is not None:
        course["is_available"] = is_available

    return course


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    course = find_course(course_id)
    if not course:
        return {"error": "Course not found"}

    courses.remove(course)
    return {"message": f"{course['title']} deleted"}


# -------------------- CART WORKFLOW --------------------

@app.post("/cart/add")
def add_to_cart(course_id: int, quantity: int = 1):
    course = find_course(course_id)
    if not course:
        return {"error": "Course not found"}

    for item in cart:
        if item["course_id"] == course_id:
            item["quantity"] += quantity
            return {"cart": cart}

    cart.append({
        "course_id": course_id,
        "title": course["title"],
        "price": course["price"],
        "quantity": quantity
    })

    return {"cart": cart}


@app.get("/cart")
def view_cart():
    total = sum(item["price"] * item["quantity"] for item in cart)
    return {"cart": cart, "total": total}


@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    global enrollment_counter

    orders = []
    total = 0

    for item in cart:
        record = {
            "id": enrollment_counter,
            "student_name": data.student_name,
            "course": item["title"],
            "quantity": item["quantity"],
            "total_price": item["price"] * item["quantity"]
        }
        enrollments.append(record)
        orders.append(record)
        total += record["total_price"]
        enrollment_counter += 1

    cart.clear()
    return {"orders": orders, "grand_total": total}


# -------------------- ENROLLMENT ADVANCED --------------------

@app.get("/enrollments/search")
def search_enroll(student_name: str):
    result = [
        e for e in enrollments
        if student_name.lower() in e["student_name"].lower()
    ]
    return {"data": result}


@app.get("/enrollments/sort")
def sort_enroll(order: str = "asc"):
    data = sorted(enrollments, key=lambda x: x["total_price"])
    if order == "desc":
        data.reverse()
    return {"data": data}
