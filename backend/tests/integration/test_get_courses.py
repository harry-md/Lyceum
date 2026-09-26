from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.courses.models import Course, CourseLevel, CourseStatus
from lyceum.users.models import Instructor, User, UserRole

pytestmark = pytest.mark.asyncio

URL = "/api/v1/courses"

LINH_ID = UUID(int=1001)
NAM_ID = UUID(int=1002)


def course_id(number: int) -> str:
    return str(UUID(int=number))


def assert_page(
    body: dict,
    expected_ids: list[int],
    *,
    total: int,
    page: int = 1,
    page_size: int = 20,
    total_pages: int = 1,
) -> None:
    assert [item["id"] for item in body["items"]] == [
        course_id(number) for number in expected_ids
    ]
    assert body["total"] == total
    assert body["page"] == page
    assert body["page_size"] == page_size
    assert body["total_pages"] == total_pages


@pytest_asyncio.fixture
async def seeded_courses(session: AsyncSession) -> None:
    users = [
        User(
            id=LINH_ID,
            username="course_test_linh",
            email="course_test_linh@example.com",
            password="unused-in-course-list-tests",
            first_name="Linh",
            last_name="Nguyen",
            dob=date(2000, 1, 1),
            role=UserRole.INSTRUCTOR,
        ),
        User(
            id=NAM_ID,
            username="course_test_nam",
            email="course_test_nam@example.com",
            password="unused-in-course-list-tests",
            first_name="Nam",
            last_name="Tran",
            dob=date(2000, 1, 1),
            role=UserRole.INSTRUCTOR,
        ),
    ]

    def make_course(
        number: int,
        title: str,
        *,
        instructor_id: UUID = LINH_ID,
        level: CourseLevel = CourseLevel.BEGINNER,
        status: CourseStatus = CourseStatus.PUBLISHED,
        price: str = "0.00",
        avg_rating: float | None = None,
        rating_count: int = 0,
        enrollment_count: int = 0,
        duration: int = 0,
        published_day: int | None = None,
    ) -> Course:
        return Course(
            id=UUID(int=number),
            instructor_id=instructor_id,
            instructor_name="Linh" if instructor_id == LINH_ID else "Nam",
            title=title,
            slug=f"course-test-{number}",
            short_description=f"Description {number}",
            thumbnail=f"https://example.com/course-{number}.png",
            level=level,
            status=status,
            price=Decimal(price),
            avg_rating=avg_rating,
            rating_count=rating_count,
            enrollment_count=enrollment_count,
            total_duration_mins=duration,
            published_at=(
                datetime(2026, 1, published_day, tzinfo=UTC)
                if published_day is not None
                else None
            ),
        )

    courses = [
        make_course(
            1,
            "Python Basics",
            avg_rating=4.5,
            rating_count=10,
            enrollment_count=100,
            duration=60,
            published_day=1,
        ),
        make_course(
            2,
            "SQL Advanced",
            instructor_id=NAM_ID,
            level=CourseLevel.ADVANCED,
            price="100.00",
            avg_rating=4.5,
            rating_count=30,
            enrollment_count=50,
            duration=120,
            published_day=3,
        ),
        make_course(
            3,
            "SQL 100%",
            level=CourseLevel.INTERMEDIATE,
            price="200.00",
            avg_rating=2.0,
            rating_count=20,
            enrollment_count=200,
            duration=180,
            published_day=2,
        ),
        make_course(
            4,
            "API_core",
            instructor_id=NAM_ID,
            price="300.00",
        ),
        make_course(
            5,
            "Python Practice",
            price="100.00",
            avg_rating=0.0,
            enrollment_count=10,
            duration=90,
            published_day=3,
        ),
        make_course(
            6,
            "Python Draft",
            status=CourseStatus.DRAFT,
            avg_rating=5.0,
            published_day=4,
        ),
        make_course(
            7,
            "Python Archived",
            status=CourseStatus.ARCHIVED,
            avg_rating=5.0,
            published_day=5,
        ),
    ]

    async with session.begin():
        session.add_all(users)
        await session.flush()

        session.add_all(
            [
                Instructor(user_id=LINH_ID),
                Instructor(user_id=NAM_ID),
            ]
        )
        await session.flush()

        session.add_all(courses)


async def test_get_courses_default(
    client: AsyncClient,
    seeded_courses: None,
) -> None:
    response = await client.get(URL)

    assert response.status_code == 200
    body = response.json()

    # Default order: id DESC; draft và archived bị loại.
    assert_page(body, [5, 4, 3, 2, 1], total=5)
    assert all(item["status"] == "published" for item in body["items"])

    first = body["items"][0]
    assert first["title"] == "Python Practice"
    assert first["instructor_id"] == str(LINH_ID)
    assert first["instructor_name"] == "Linh"
    assert first["slug"] == "course-test-5"
    assert first["short_description"] == "Description 5"
    assert first["thumbnail"] == "https://example.com/course-5.png"
    assert first["level"] == "beginner"
    assert Decimal(first["price"]) == Decimal("100.00")
    assert first["avg_rating"] == 0.0
    assert first["rating_count"] == 0
    assert first["enrollment_count"] == 10
    assert first["total_duration_mins"] == 90


async def test_get_courses_empty_database(client: AsyncClient) -> None:
    response = await client.get(URL)

    assert response.status_code == 200
    assert_page(response.json(), [], total=0, total_pages=0)


@pytest.mark.parametrize(
    ("page", "expected_ids"),
    [
        (1, [5, 4]),
        (2, [3, 2]),
        (3, [1]),
        (4, []),
    ],
)
async def test_get_courses_pagination(
    client: AsyncClient,
    seeded_courses: None,
    page: int,
    expected_ids: list[int],
) -> None:
    response = await client.get(
        URL,
        params={"page": page, "page_size": 2},
    )

    assert response.status_code == 200
    assert_page(
        response.json(),
        expected_ids,
        total=5,
        page=page,
        page_size=2,
        total_pages=3,
    )


@pytest.mark.parametrize(
    ("keyword", "expected_ids"),
    [
        ("python", [5, 1]),
        ("  pYtHoN  ", [5, 1]),
        ("linh", [5, 3, 1]),
        ("NAM", [4, 2]),
        ("sql", [3, 2]),
        ("%", [3]),
        ("_", [4]),
        ("does-not-exist", []),
        ("   ", [5, 4, 3, 2, 1]),
    ],
)
async def test_search_courses(
    client: AsyncClient,
    seeded_courses: None,
    keyword: str,
    expected_ids: list[int],
) -> None:
    response = await client.get(URL, params={"keyword": keyword})

    assert response.status_code == 200
    assert_page(
        response.json(),
        expected_ids,
        total=len(expected_ids),
        total_pages=1 if expected_ids else 0,
    )


async def test_search_courses_total_is_not_page_length(
    client: AsyncClient,
    seeded_courses: None,
) -> None:
    response = await client.get(
        URL,
        params={"keyword": "python", "page_size": 1},
    )

    assert response.status_code == 200
    assert_page(
        response.json(),
        [5],
        total=2,
        page_size=1,
        total_pages=2,
    )


@pytest.mark.parametrize(
    ("order_by", "expected_ids"),
    [
        ("avg_rating", [2, 1, 3, 5, 4]),
        ("rating_count", [2, 3, 1, 5, 4]),
        ("enrollment_count", [3, 1, 2, 5, 4]),
        ("published_at", [5, 2, 3, 1, 4]),
    ],
)
async def test_sort_courses(
    client: AsyncClient,
    seeded_courses: None,
    order_by: str,
    expected_ids: list[int],
) -> None:
    response = await client.get(URL, params={"order_by": order_by})

    assert response.status_code == 200

    # Các giá trị giảm dần, NULL cuối, bằng nhau thì id DESC.
    assert_page(response.json(), expected_ids, total=5)


@pytest.mark.parametrize(
    ("page", "expected_ids"),
    [
        (1, [2]),
        (2, [1]),
    ],
)
async def test_sort_courses_before_pagination(
    client: AsyncClient,
    seeded_courses: None,
    page: int,
    expected_ids: list[int],
) -> None:
    response = await client.get(
        URL,
        params={
            "order_by": "avg_rating",
            "page": page,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    assert_page(
        response.json(),
        expected_ids,
        total=5,
        page=page,
        page_size=1,
        total_pages=5,
    )


@pytest.mark.parametrize(
    ("params", "expected_ids"),
    [
        ({"instructor_id": str(LINH_ID)}, [5, 3, 1]),
        ({"instructor_id": str(UUID(int=9999))}, []),
        ({"level": "beginner"}, [5, 4, 1]),
        ({"level": "advanced"}, [2]),
        ({"from_price": "100.00"}, [5, 4, 3, 2]),
        ({"to_price": "100.00"}, [5, 2, 1]),
        ({"from_price": "100.00", "to_price": "100.00"}, [5, 2]),
        ({"to_price": "0.00"}, [1]),
        ({"from_rating": 4}, [2, 1]),
        ({"to_rating": 2}, [5, 3]),
        ({"from_rating": 2, "to_rating": 2}, [3]),
        ({"from_rating": 0}, [5, 3, 2, 1]),
        ({"to_rating": 0}, [5]),
        ({"from_duration_mins": 90}, [5, 3, 2]),
        ({"to_duration_mins": 90}, [5, 4, 1]),
        ({"from_duration_mins": 90, "to_duration_mins": 90}, [5]),
        ({"to_duration_mins": 0}, [4]),
    ],
)
async def test_filter_courses(
    client: AsyncClient,
    seeded_courses: None,
    params: dict,
    expected_ids: list[int],
) -> None:
    response = await client.get(URL, params=params)

    assert response.status_code == 200
    assert_page(
        response.json(),
        expected_ids,
        total=len(expected_ids),
        total_pages=1 if expected_ids else 0,
    )


async def test_combine_search_filters_sort_and_pagination(
    client: AsyncClient,
    seeded_courses: None,
) -> None:
    response = await client.get(
        URL,
        params={
            "keyword": "python",
            "instructor_id": str(LINH_ID),
            "level": "beginner",
            "from_price": "0.00",
            "to_price": "100.00",
            "from_duration_mins": 60,
            "to_duration_mins": 90,
            "order_by": "avg_rating",
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    assert_page(
        response.json(),
        [1],
        total=2,
        page_size=1,
        total_pages=2,
    )


async def test_filters_are_combined_with_and(
    client: AsyncClient,
    seeded_courses: None,
) -> None:
    # Có khóa học Python, có giảng viên Nam,
    # nhưng không có khóa học Python của Nam.
    response = await client.get(
        URL,
        params={
            "keyword": "python",
            "instructor_id": str(NAM_ID),
        },
    )

    assert response.status_code == 200
    assert_page(response.json(), [], total=0, total_pages=0)


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": "abc"},
        {"page_size": 0},
        {"page_size": 51},
        {"keyword": ""},
        {"keyword": "a" * 201},
        {"instructor_id": "not-a-uuid"},
        {"level": "expert"},
        {"order_by": "price"},
        {"from_price": "-1"},
        {"to_price": "-1"},
        {"from_price": "1.001"},
        {"from_price": "100000000.00"},
        {"from_rating": -1},
        {"to_rating": 6},
        {"from_duration_mins": -1},
        {"to_duration_mins": -1},
        {"from_price": "200.00", "to_price": "100.00"},
        {"from_rating": 5, "to_rating": 4},
        {"from_duration_mins": 120, "to_duration_mins": 60},
    ],
)
async def test_get_courses_invalid_query(
    client: AsyncClient,
    params: dict,
) -> None:
    response = await client.get(URL, params=params)

    assert response.status_code == 422
