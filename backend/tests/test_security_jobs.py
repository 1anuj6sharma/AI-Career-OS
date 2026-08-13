def test_unauthenticated_access_denied(client):
    res_jobs = client.get("/api/v1/jobs")
    assert res_jobs.status_code == 401

    res_apps = client.get("/api/v1/applications")
    assert res_apps.status_code == 401

    res_contacts = client.get("/api/v1/contacts")
    assert res_contacts.status_code == 401


def test_user_ownership_isolation(client, auth_headers, auth_headers_b):
    # User A creates a job and application
    j_res = client.post(
        "/api/v1/jobs",
        json={"title": "Confidential Role User A"},
        headers=auth_headers,
    )
    job_id_a = j_res.json()["id"]

    app_res = client.post(
        f"/api/v1/jobs/{job_id_a}/applications",
        json={"status": "SAVED"},
        headers=auth_headers,
    )
    app_id_a = app_res.json()["id"]

    # User B attempts to access User A's job -> 404 (or 403)
    get_b_job = client.get(f"/api/v1/jobs/{job_id_a}", headers=auth_headers_b)
    assert get_b_job.status_code == 404

    # User B attempts to modify User A's job -> 404
    patch_b_job = client.patch(
        f"/api/v1/jobs/{job_id_a}",
        json={"title": "Hacked Title"},
        headers=auth_headers_b,
    )
    assert patch_b_job.status_code == 404

    # User B attempts to delete User A's job -> 404
    del_b_job = client.delete(f"/api/v1/jobs/{job_id_a}", headers=auth_headers_b)
    assert del_b_job.status_code == 404

    # User B attempts to access User A's application -> 404
    get_b_app = client.get(
        f"/api/v1/applications/{app_id_a}", headers=auth_headers_b
    )
    assert get_b_app.status_code == 404
