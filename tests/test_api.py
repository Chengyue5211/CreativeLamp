"""
绘创前程 — 全面API测试套件
覆盖: 认证安全/IDOR/文件上传/速率限制/业务流程
"""
import sys
import os
import io
import json
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from main import app
from core.database import get_db, init_database
from core.security import hash_password, _token_blacklist, _rate_limits


@pytest.fixture(autouse=True)
def clean_rate_limits():
    """每个测试前清空速率限制"""
    _rate_limits.clear()
    _token_blacklist.clear()
    yield
    _rate_limits.clear()
    _token_blacklist.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_phone():
    """生成唯一测试手机号"""
    return f"138{int(time.time() * 1000) % 100000000:08d}"


@pytest.fixture
def parent_token(client, test_phone):
    """注册并获取家长token"""
    resp = client.post("/api/auth/register", json={
        "phone": test_phone, "password": "test123456", "nickname": "TestParent"
    })
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture
def child_token(client, parent_token):
    """添加孩子并获取孩子token"""
    # 添加孩子
    resp = client.post("/api/auth/children", json={
        "nickname": "TestChild", "age": 7, "gender": "male"
    }, headers={"Authorization": f"Bearer {parent_token}"})
    assert resp.status_code == 200
    child_id = resp.json()["child_id"]
    # 切换到孩子
    resp = client.post(f"/api/auth/switch-child/{child_id}",
                       headers={"Authorization": f"Bearer {parent_token}"})
    assert resp.status_code == 200
    return resp.json()["token"], child_id


# ============================================================
# 1. 认证安全测试
# ============================================================
class TestAuthSecurity:
    def test_register_success(self, client, test_phone):
        resp = client.post("/api/auth/register", json={
            "phone": test_phone, "password": "test123", "nickname": "Test"
        })
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_register_duplicate_phone(self, client, test_phone):
        client.post("/api/auth/register", json={
            "phone": test_phone, "password": "test123"
        })
        resp = client.post("/api/auth/register", json={
            "phone": test_phone, "password": "test123"
        })
        assert resp.status_code == 400
        assert "已注册" in resp.json()["detail"]

    def test_register_invalid_phone(self, client):
        resp = client.post("/api/auth/register", json={
            "phone": "12345", "password": "test123"
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client, test_phone):
        resp = client.post("/api/auth/register", json={
            "phone": test_phone, "password": "12345"
        })
        assert resp.status_code == 422

    def test_login_success(self, client, test_phone):
        client.post("/api/auth/register", json={
            "phone": test_phone, "password": "test123"
        })
        resp = client.post("/api/auth/login", json={
            "phone": test_phone, "password": "test123"
        })
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_login_wrong_password(self, client, test_phone):
        client.post("/api/auth/register", json={
            "phone": test_phone, "password": "test123"
        })
        resp = client.post("/api/auth/login", json={
            "phone": test_phone, "password": "wrong!!"
        })
        assert resp.status_code == 400

    def test_login_nonexistent_phone(self, client):
        resp = client.post("/api/auth/login", json={
            "phone": "13999999999", "password": "test123"
        })
        assert resp.status_code == 400

    def test_logout_invalidates_token(self, client, parent_token):
        # Token works before logout
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        # Logout
        resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        # Token should be blacklisted
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 401

    def test_no_auth_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_get_me_returns_user(self, client, parent_token):
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "nickname" in data
        assert "password_hash" not in data


# ============================================================
# 2. 速率限制测试
# ============================================================
class TestRateLimiting:
    def test_login_rate_limit(self, client):
        """10次/分钟后应该被限制"""
        for i in range(10):
            client.post("/api/auth/login", json={"phone": "13800000000", "password": "x"})
        resp = client.post("/api/auth/login", json={"phone": "13800000000", "password": "x"})
        assert resp.status_code == 429

    def test_register_rate_limit(self, client):
        """5次/分钟后应该被限制"""
        for i in range(5):
            client.post("/api/auth/register", json={
                "phone": f"1380000{i:04d}", "password": "test123"
            })
        resp = client.post("/api/auth/register", json={
            "phone": "13800009999", "password": "test123"
        })
        assert resp.status_code == 429


# ============================================================
# 3. IDOR测试
# ============================================================
class TestIDOR:
    def test_switch_to_unowned_child(self, client, parent_token):
        """家长不能切换到不属于自己的孩子"""
        resp = client.post("/api/auth/switch-child/99999",
                           headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 403

    def test_child_cannot_see_other_child_works(self, client, child_token):
        """孩子不能看其他孩子的作品"""
        token, child_id = child_token
        resp = client.get("/api/works/99999",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_parent_cannot_see_unrelated_child_works(self, client):
        """家长不能看非自己孩子的作品"""
        # 注册两个家长
        phone1 = f"138{int(time.time()*1000) % 100000000:08d}"
        time.sleep(0.01)
        phone2 = f"138{int(time.time()*1000) % 100000000:08d}"

        r1 = client.post("/api/auth/register", json={"phone": phone1, "password": "test123"})
        token1 = r1.json()["token"]
        r2 = client.post("/api/auth/register", json={"phone": phone2, "password": "test123"})
        token2 = r2.json()["token"]

        # 家长1添加孩子
        r = client.post("/api/auth/children", json={"nickname": "Child1", "age": 7},
                       headers={"Authorization": f"Bearer {token1}"})
        child1_id = r.json()["child_id"]

        # 家长2不能查看家长1的孩子作品
        resp = client.get(f"/api/parent/child/{child1_id}/works",
                         headers={"Authorization": f"Bearer {token2}"})
        assert resp.status_code == 403


# ============================================================
# 4. 文件上传安全测试
# ============================================================
class TestUploadSecurity:
    def test_upload_valid_image(self, client, child_token):
        """上传合法图片"""
        token, _ = child_token
        # 创建一个最小的有效PNG
        from PIL import Image
        img = Image.new("RGB", (100, 100), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        resp = client.post("/api/works/upload",
            files={"image": ("test.png", buf, "image/png")},
            data={"title": "Test Work"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert "work_id" in resp.json()

    def test_upload_invalid_mime(self, client, child_token):
        """拒绝非图片MIME类型"""
        token, _ = child_token
        resp = client.post("/api/works/upload",
            files={"image": ("test.txt", b"not an image", "text/plain")},
            data={"title": "Hack"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 400

    def test_upload_fake_mime(self, client, child_token):
        """拒绝MIME伪造（声称image/png但内容不是图片）"""
        token, _ = child_token
        resp = client.post("/api/works/upload",
            files={"image": ("evil.png", b"this is not a real png", "image/png")},
            data={"title": "Fake"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 400

    def test_upload_requires_auth(self, client):
        """上传需要认证"""
        resp = client.post("/api/works/upload",
            files={"image": ("test.png", b"x", "image/png")},
            data={"title": "Test"}
        )
        assert resp.status_code == 401

    def test_path_traversal_work_image(self, client):
        """路径穿越攻击应被拒绝"""
        resp = client.get("/api/works/image/..%2F..%2F..%2Fetc%2Fpasswd")
        assert resp.status_code in (400, 404)

    def test_path_traversal_contour_image(self, client):
        """轮廓图路径穿越应被拒绝"""
        resp = client.get("/api/contours/image/..%2Fetc%2Fpasswd")
        assert resp.status_code in (400, 404)


# ============================================================
# 5. 安全响应头测试
# ============================================================
class TestSecurityHeaders:
    def test_x_content_type_options(self, client):
        resp = client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, client):
        resp = client.get("/health")
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, client):
        resp = client.get("/health")
        assert "strict-origin" in resp.headers.get("referrer-policy", "")


# ============================================================
# 6. 训练系统业务测试
# ============================================================
class TestTraining:
    def test_list_prototypes(self, client):
        resp = client.get("/api/training/prototypes")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 100

    def test_list_transforms(self, client):
        resp = client.get("/api/training/transforms")
        assert resp.status_code == 200
        assert resp.json()["total"] == 7

    def test_list_contours(self, client):
        resp = client.get("/api/training/contours")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 44
        # 每个轮廓应该有image_url
        for c in data["contours"]:
            assert "image_url" in c

    def test_list_levels(self, client):
        resp = client.get("/api/training/levels")
        assert resp.status_code == 200

    def test_generate_daily_task(self, client, child_token):
        token, _ = child_token
        resp = client.post("/api/training/daily-task",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data

    def test_parent_cannot_generate_task(self, client, parent_token):
        resp = client.post("/api/training/daily-task",
                          headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 400

    def test_get_today_tasks(self, client, child_token):
        token, _ = child_token
        resp = client.get("/api/training/today",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_task_history(self, client, child_token):
        token, _ = child_token
        resp = client.get("/api/training/history",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "total" in data
        assert "page" in data


# ============================================================
# 7. 作品系统业务测试
# ============================================================
class TestWorks:
    def test_my_works(self, client, child_token):
        token, _ = child_token
        resp = client.get("/api/works/my",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert "works" in resp.json()

    def test_upload_and_view(self, client, child_token):
        """完整流程：上传 -> 查看详情"""
        token, _ = child_token
        from PIL import Image
        img = Image.new("RGB", (50, 50), "blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        # 上传
        resp = client.post("/api/works/upload",
            files={"image": ("art.jpg", buf, "image/jpeg")},
            data={"title": "My Art"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        work_id = resp.json()["work_id"]

        # 查看
        resp = client.get(f"/api/works/{work_id}",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "My Art"

    def test_evaluate_work(self, client, child_token, parent_token):
        """家长评价作品"""
        token, child_id = child_token
        from PIL import Image
        img = Image.new("RGB", (50, 50), "green")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        resp = client.post("/api/works/upload",
            files={"image": ("eval.png", buf, "image/png")},
            data={"title": "Evaluate Me"},
            headers={"Authorization": f"Bearer {token}"}
        )
        work_id = resp.json()["work_id"]

        # 家长评价
        resp = client.post(f"/api/works/{work_id}/evaluate",
            json={"originality": 8.5, "detail": 7.0, "composition": 8.0, "expression": 9.0, "feedback": "Great work!"},
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["scores"]["average"] > 0

    def test_evaluate_score_validation(self, client, child_token):
        """评分范围校验"""
        token, _ = child_token
        from PIL import Image
        img = Image.new("RGB", (10, 10), "red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("x.png", buf, "image/png")},
            data={"title": "X"},
            headers={"Authorization": f"Bearer {token}"}
        )
        work_id = resp.json()["work_id"]

        # 超出范围
        resp = client.post(f"/api/works/{work_id}/evaluate",
            json={"originality": 15, "detail": 7, "composition": 7, "expression": 7},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 422


# ============================================================
# 8. 展示系统测试
# ============================================================
class TestShowcase:
    def test_growth_archive(self, client, child_token):
        token, _ = child_token
        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "child" in data
        assert "stats" in data


# ============================================================
# 9. 家长系统测试
# ============================================================
class TestParent:
    def test_dashboard(self, client, parent_token):
        resp = client.get("/api/parent/dashboard",
                         headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        assert "children" in resp.json()

    def test_child_works_pagination(self, client, parent_token, child_token):
        _, child_id = child_token
        resp = client.get(f"/api/parent/child/{child_id}/works?page=1&limit=5",
                         headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "page" in data
        assert "pages" in data
        assert "total" in data

    def test_child_requires_parent(self, client, child_token):
        token, _ = child_token
        resp = client.get("/api/parent/dashboard",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


# ============================================================
# 10. 未实现端点测试
# ============================================================
class TestStubs:
    def test_merch_types_public(self, client):
        resp = client.get("/api/merch/types")
        assert resp.status_code == 200

    def test_merch_preview_requires_auth(self, client):
        resp = client.post("/api/merch/preview")
        assert resp.status_code in (401, 422)

    def test_merch_order_requires_auth(self, client):
        resp = client.post("/api/merch/order")
        assert resp.status_code in (401, 422)

    def test_referral_code_requires_auth(self, client):
        resp = client.get("/api/referral/my-code")
        assert resp.status_code == 401

    def test_referral_rewards_requires_auth(self, client):
        resp = client.get("/api/referral/rewards")
        assert resp.status_code == 401


# ============================================================
# 11. 健康检查
# ============================================================
class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ============================================================
# 12. 端到端流程测试
# ============================================================
class TestE2EFlow:
    def test_full_training_cycle(self, client, child_token, parent_token):
        """完整训练周期：生成任务 -> 查历史获取task_id -> 开始 -> 上传作品 -> 评价"""
        token, child_id = child_token

        # 生成任务
        resp = client.post("/api/training/daily-task",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        gen_data = resp.json()
        gen_tasks = gen_data.get("tasks", [])
        assert len(gen_tasks) > 0, "daily-task should generate at least one task"

        # 通过任务历史获取已持久化的task_id
        # (注意: /today 端点依赖时区对齐，在UTC+8环境可能不匹配SQLite的UTC时间)
        resp = client.get("/api/training/history?page=1&limit=5",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        history_tasks = resp.json().get("tasks", [])
        assert len(history_tasks) > 0, "task history should contain generated tasks"
        task_id = history_tasks[0]["id"]

        # 开始任务
        resp = client.post(f"/api/training/task/{task_id}/status?status=in_progress",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

        # 上传作品关联任务
        from PIL import Image
        img = Image.new("RGB", (80, 80), "purple")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("task_art.png", buf, "image/png")},
            data={"title": "Task Artwork", "task_id": str(task_id)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        work_id = resp.json()["work_id"]

        # 家长评价
        resp = client.post(f"/api/works/{work_id}/evaluate",
            json={"originality": 9, "detail": 8, "composition": 8.5, "expression": 9.5, "feedback": "Excellent!"},
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert resp.status_code == 200

        # 查看成长档案
        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
