import itertools
import os
import random

from locust import HttpUser, between, constant, task

_counter = itertools.count(1)

# Năm xuất bản dùng cho tạo sách và tìm kiếm — trùng nhau để search có kết quả.
YEARS = list(range(2000, 2025))
INJECTED_FAILURE_RATE = 0.01


class BooksUser(HttpUser):
    # Mặc định: think time 1-3s như starter. LOCUST_NO_WAIT=1 bỏ think time để
    # dồn request đồng thời (dùng cho câu bonus về connection pool).
    wait_time = constant(0) if os.environ.get("LOCUST_NO_WAIT") == "1" else between(1, 3)

    @task(3)
    def list_books(self):
        self.client.get("/books", name="GET /books")

    @task(2)
    def read_book(self):
        book_id = random.randint(1, 50)
        with self.client.get(
            f"/books/{book_id}", name="GET /books/{id}", catch_response=True
        ) as response:
            # Expected 404 (random id absent) is not an operational failure.
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def create_book(self):
        unique = next(_counter)
        self.client.post(
            "/books",
            json={"title": f"Load test {unique}", "author": "locust",
                  "year": random.choice(YEARS)},
            name="POST /books",
        )

    @task(2)
    def search_by_year(self):
        self._search_by_year(random.choice(YEARS))

    def _search_by_year(self, year):
        with self.client.get(
            "/books", params={"year": year},
            name="GET /books?year=[year]", catch_response=True,
        ) as response:
            if response.status_code != 200:
                # Lỗi thật từ server (vd. 500, 400) — giữ nguyên status để phân biệt.
                response.failure(f"REAL HTTP {response.status_code}")
                return
            books = response.json()
            if not isinstance(books, list) or any(b.get("year") != year for b in books):
                response.failure("Wrong body: expected list of books with matching year")
                return
            if random.random() < INJECTED_FAILURE_RATE:
                # Client-side, không phải lỗi server.
                response.failure("INJECTED 1% client-side failure (simulated 500)")
                return
            response.success()
