def test_company_and_contact_crud(client, auth_headers):
    # Create Company
    comp_res = client.post(
        "/api/v1/companies",
        json={"name": "Google", "website": "https://google.com", "size": "500+"},
        headers=auth_headers,
    )
    assert comp_res.status_code == 201
    comp_id = comp_res.json()["id"]

    # Create Contact
    contact_res = client.post(
        "/api/v1/contacts",
        json={
            "company_id": comp_id,
            "name": "Sarah Connor",
            "email": "sarah@google.com",
            "designation": "Technical Recruiter",
        },
        headers=auth_headers,
    )
    assert contact_res.status_code == 201
    contact_data = contact_res.json()
    assert contact_data["name"] == "Sarah Connor"
    assert contact_data["company"]["name"] == "Google"


def test_task_management(client, auth_headers):
    j = client.post("/api/v1/jobs", json={"title": "SDE-2"}, headers=auth_headers).json()["id"]
    app_id = client.post(f"/api/v1/jobs/{j}/applications", json={"status": "APPLIED"}, headers=auth_headers).json()["id"]

    # Create Task
    task_res = client.post(
        f"/api/v1/applications/{app_id}/tasks",
        json={
            "title": "Revise System Design",
            "priority": "HIGH",
            "status": "PENDING",
        },
        headers=auth_headers,
    )
    assert task_res.status_code == 201
    task_id = task_res.json()["id"]

    # Complete Task
    update_res = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "COMPLETED"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "COMPLETED"
    assert update_res.json()["completed_at"] is not None
