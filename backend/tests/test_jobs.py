def test_create_and_get_job(client, auth_headers):
    payload = {
        "title": "Senior Python Developer",
        "company_name": "Tech Corp",
        "description": "Building scalable backend services with FastAPI and PostgreSQL",
        "location": "San Francisco, CA",
        "remote_type": "REMOTE",
        "employment_type": "FULL_TIME",
        "experience_level": "SENIOR",
        "salary_min": 130000,
        "salary_max": 160000,
        "currency": "USD",
        "source": "LinkedIn",
        "is_favorite": True,
    }
    response = client.post("/api/v1/jobs", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Python Developer"
    assert data["company_name"] == "Tech Corp"
    assert data["is_favorite"] is True
    job_id = data["id"]

    # Get Job
    get_res = client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id


def test_update_and_delete_job(client, auth_headers):
    create_res = client.post(
        "/api/v1/jobs",
        json={"title": "Backend Engineer", "company_name": "Startup Inc"},
        headers=auth_headers,
    )
    job_id = create_res.json()["id"]

    # Patch job
    patch_res = client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"title": "Lead Backend Engineer", "is_archived": True},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Lead Backend Engineer"
    assert patch_res.json()["is_archived"] is True

    # Delete job
    del_res = client.delete(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify not found
    get_res = client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_list_search_filter_jobs(client, auth_headers):
    client.post(
        "/api/v1/jobs",
        json={
            "title": "React Frontend Developer",
            "company_name": "Design Systems",
            "location": "New York",
            "remote_type": "ONSITE",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/jobs",
        json={
            "title": "Python Data Engineer",
            "company_name": "Data Systems",
            "location": "Remote",
            "remote_type": "REMOTE",
        },
        headers=auth_headers,
    )

    # Search query
    res = client.get("/api/v1/jobs?search=Python", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Data Engineer"

    # Filter remote
    res_remote = client.get("/api/v1/jobs?remote_type=REMOTE", headers=auth_headers)
    assert res_remote.status_code == 200
    assert res_remote.json()["total"] == 1


def test_salary_validation(client, auth_headers):
    # Invalid salary (min > max)
    payload = {
        "title": "DevOps Engineer",
        "salary_min": 150000,
        "salary_max": 100000,
    }
    res = client.post("/api/v1/jobs", json=payload, headers=auth_headers)
    assert res.status_code == 422
