def test_application_lifecycle_and_timeline(client, auth_headers):
    # 1. Create Job
    job_res = client.post(
        "/api/v1/jobs",
        json={"title": "Software Engineer", "company_name": "Acme Corp"},
        headers=auth_headers,
    )
    job_id = job_res.json()["id"]

    # 2. Create Application
    app_res = client.post(
        f"/api/v1/jobs/{job_id}/applications",
        json={"status": "SAVED", "notes": "Interested in distributed systems team"},
        headers=auth_headers,
    )
    assert app_res.status_code == 201
    app_data = app_res.json()
    app_id = app_data["id"]
    assert app_data["status"] == "SAVED"
    assert len(app_data["events"]) >= 1

    # 3. Update Status to INTERVIEW (Atomic status update + timeline event)
    status_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "INTERVIEW", "description": "Scheduled technical interview"},
        headers=auth_headers,
    )
    assert status_res.status_code == 200
    updated_app = status_res.json()
    assert updated_app["status"] == "INTERVIEW"

    # 4. Check Timeline
    timeline_res = client.get(
        f"/api/v1/applications/{app_id}/timeline", headers=auth_headers
    )
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert len(events) >= 2
    event_types = [e["event_type"] for e in events]
    assert "STATUS_CHANGE" in event_types


def test_list_applications_by_status(client, auth_headers):
    j1 = client.post(
        "/api/v1/jobs", json={"title": "Job 1"}, headers=auth_headers
    ).json()["id"]
    j2 = client.post(
        "/api/v1/jobs", json={"title": "Job 2"}, headers=auth_headers
    ).json()["id"]

    client.post(
        f"/api/v1/jobs/{j1}/applications",
        json={"status": "APPLIED"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/jobs/{j2}/applications",
        json={"status": "OFFER"},
        headers=auth_headers,
    )

    res_offer = client.get(
        "/api/v1/applications?status=OFFER", headers=auth_headers
    )
    assert res_offer.status_code == 200
    assert res_offer.json()["total"] == 1
    assert res_offer.json()["items"][0]["status"] == "OFFER"
