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

    def test_login_invalid_phone_format(self, client):
        """手机号格式不合法应返回422"""
        resp = client.post("/api/auth/login", json={
            "phone": "abc", "password": "test123"
        })
        assert resp.status_code == 422

    def test_list_children(self, client, parent_token):
        """家长获取孩子列表"""
        resp = client.get("/api/auth/children",
                          headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        assert "children" in resp.json()

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
            client.post("/api/auth/login", json={"phone": "13800000000", "password": "wrong123"})
        resp = client.post("/api/auth/login", json={"phone": "13800000000", "password": "wrong123"})
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

    def test_list_increase_subtypes(self, client):
        """获取增加动作的5种子类型"""
        resp = client.get("/api/training/increase-subtypes")
        assert resp.status_code == 200
        data = resp.json()
        assert "subtypes" in data or isinstance(data, list) or len(data) > 0

    def test_list_task_types(self, client):
        """获取任务类型说明"""
        resp = client.get("/api/training/task-types")
        assert resp.status_code == 200
        data = resp.json()
        assert "task_types" in data
        assert len(data["task_types"]) > 0

    def test_get_task_detail(self, client, child_token):
        """获取任务详情（需先生成任务）"""
        token, _ = child_token
        # 先生成任务
        client.post("/api/training/daily-task",
                    headers={"Authorization": f"Bearer {token}"})
        # 从历史获取task_id
        resp = client.get("/api/training/history?page=1&limit=1",
                         headers={"Authorization": f"Bearer {token}"})
        tasks = resp.json().get("tasks", [])
        assert len(tasks) > 0
        task_id = tasks[0]["id"]
        # 获取详情
        resp = client.get(f"/api/training/task/{task_id}",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_get_task_detail_nonexistent(self, client, child_token):
        """获取不存在的任务应返回404"""
        token, _ = child_token
        resp = client.get("/api/training/task/999999",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


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

    def test_edit_work(self, client, child_token):
        """编辑作品标题和描述"""
        token, _ = child_token
        from PIL import Image
        img = Image.new("RGB", (30, 30), "yellow")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("edit_test.png", buf, "image/png")},
            data={"title": "Original Title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        work_id = resp.json()["work_id"]

        # 编辑
        resp = client.put(f"/api/works/{work_id}/edit",
            data={"title": "New Title", "description": "New Description"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["work_id"] == work_id

    def test_edit_work_empty_body(self, client, child_token):
        """编辑作品时不传任何字段应优雅处理"""
        token, _ = child_token
        from PIL import Image
        img = Image.new("RGB", (30, 30), "cyan")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("empty_edit.png", buf, "image/png")},
            data={"title": "No Change"},
            headers={"Authorization": f"Bearer {token}"}
        )
        work_id = resp.json()["work_id"]

        # 不传title和description
        resp = client.put(f"/api/works/{work_id}/edit",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200

    def test_upload_oversized_title(self, client, child_token):
        """上传时标题超长应被截断或拒绝"""
        token, _ = child_token
        from PIL import Image
        img = Image.new("RGB", (30, 30), "pink")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        long_title = "A" * 200  # 超过max_length=100
        resp = client.post("/api/works/upload",
            files={"image": ("long_title.png", buf, "image/png")},
            data={"title": long_title},
            headers={"Authorization": f"Bearer {token}"}
        )
        # 应返回422(验证失败)或200(截断处理)
        assert resp.status_code in (200, 422)


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

    def test_update_work_visibility(self, client, parent_token, child_token):
        """家长更改作品可见性"""
        token, child_id = child_token
        from PIL import Image
        img = Image.new("RGB", (30, 30), "orange")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("vis.png", buf, "image/png")},
            data={"title": "Visibility Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        work_id = resp.json()["work_id"]

        # 家长设置为public
        resp = client.put(f"/api/parent/work/{work_id}/visibility",
            params={"visibility": "public"},
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["visibility"] == "public"

    def test_mark_work_as_candidate(self, client, parent_token, child_token):
        """家长标记作品为候选"""
        token, child_id = child_token
        from PIL import Image
        img = Image.new("RGB", (30, 30), "brown")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("cand.png", buf, "image/png")},
            data={"title": "Candidate Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        work_id = resp.json()["work_id"]

        # 家长标记为文创候选
        resp = client.put(f"/api/parent/work/{work_id}/candidate",
            params={"merch": True},
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert resp.status_code == 200


# ============================================================
# 10. 未实现端点测试
# ============================================================
class TestMerchSystem:
    """文创系统完整测试"""

    def _upload_work(self, client, child_token):
        """辅助：上传一个作品，返回 work_id"""
        from PIL import Image
        img = Image.new("RGB", (50, 50), "blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("merch_test.png", buf, "image/png")},
            data={"title": "Merch Test Art"},
            headers={"Authorization": f"Bearer {child_token}"},
        )
        assert resp.status_code == 200
        return resp.json()["work_id"]

    def test_merch_types_public(self, client):
        """文创产品列表无需认证"""
        resp = client.get("/api/merch/types")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 7
        assert any(t["id"] == "postcard" for t in data["merch_types"])

    def test_merch_types_have_price(self, client):
        """产品列表包含价格信息"""
        resp = client.get("/api/merch/types")
        types = resp.json()["merch_types"]
        for t in types:
            assert "base_price" in t
            assert "price_display" in t
            assert t["base_price"] > 0

    def test_merch_order_requires_auth(self, client):
        """下单需要认证"""
        resp = client.post("/api/merch/order", json={
            "merch_type_id": "postcard", "work_ids": [1]
        })
        assert resp.status_code == 401

    def test_merch_orders_requires_auth(self, client):
        """订单列表需要认证"""
        resp = client.get("/api/merch/orders")
        assert resp.status_code == 401

    def test_merch_order_success(self, client, child_token, parent_token):
        """成功下单"""
        token, _ = child_token
        work_id = self._upload_work(client, token)
        resp = client.post("/api/merch/order",
            json={"merch_type_id": "postcard", "work_ids": [work_id]},
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["order_id"] > 0
        assert data["merch_type"] == "明信片"
        assert data["total_price"] == 500
        assert data["credits_used"] == 0
        assert data["amount_due"] == 500

    def test_merch_order_with_credit_deduction(self, client, child_token):
        """学币抵扣下单"""
        token, _ = child_token
        work_id = self._upload_work(client, token)

        # 先给该家长充点学币：通过推荐
        ts = int(time.time() * 1000) % 100000000
        # 注册一个新家长，拿到他的 parent_token
        resp = client.post("/api/auth/register", json={
            "phone": f"136{ts:08d}", "password": "test123456", "nickname": "CreditTestParent"
        })
        credit_parent_token = resp.json()["token"]
        credit_parent_id = resp.json()["user_id"]

        # 添加孩子并上传作品
        resp = client.post("/api/auth/children", json={
            "nickname": "CreditChild", "age": 6, "gender": "male"
        }, headers={"Authorization": f"Bearer {credit_parent_token}"})
        credit_child_id = resp.json()["child_id"]
        resp = client.post(f"/api/auth/switch-child/{credit_child_id}",
            headers={"Authorization": f"Bearer {credit_parent_token}"})
        credit_child_token = resp.json()["token"]

        from PIL import Image
        img = Image.new("RGB", (50, 50), "green")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("credit_art.png", buf, "image/png")},
            data={"title": "Credit Art"},
            headers={"Authorization": f"Bearer {credit_child_token}"},
        )
        credit_work_id = resp.json()["work_id"]

        # 手动加学币
        from core.database import get_db
        with get_db() as conn:
            conn.execute("UPDATE users SET credit_balance = 200 WHERE id = ?", (credit_parent_id,))

        # 下单并抵扣
        resp = client.post("/api/merch/order",
            json={"merch_type_id": "postcard", "work_ids": [credit_work_id], "use_credits": 200},
            headers={"Authorization": f"Bearer {credit_parent_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["credits_used"] == 200
        assert data["amount_due"] == 300  # 500 - 200

        # 验证学币已扣
        resp = client.get("/api/referral/balance",
            headers={"Authorization": f"Bearer {credit_parent_token}"})
        assert resp.json()["credit_balance"] == 0

    def test_merch_order_invalid_type(self, client, child_token, parent_token):
        """无效产品类型"""
        token, _ = child_token
        work_id = self._upload_work(client, token)
        resp = client.post("/api/merch/order",
            json={"merch_type_id": "nonexistent", "work_ids": [work_id]},
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert resp.status_code == 404

    def test_merch_order_other_child_work(self, client, parent_token):
        """不能用别人孩子的作品下单"""
        resp = client.post("/api/merch/order",
            json={"merch_type_id": "postcard", "work_ids": [99999]},
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert resp.status_code == 403

    def test_merch_orders_list(self, client, child_token, parent_token):
        """订单列表"""
        token, _ = child_token
        work_id = self._upload_work(client, token)
        client.post("/api/merch/order",
            json={"merch_type_id": "sticker", "work_ids": [work_id]},
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        resp = client.get("/api/merch/orders",
            headers={"Authorization": f"Bearer {parent_token}"})
        assert resp.status_code == 200
        orders = resp.json()["orders"]
        assert len(orders) >= 1

    def test_merch_credit_cap(self, client, child_token):
        """学币抵扣不超过产品价格"""
        token, _ = child_token
        work_id = self._upload_work(client, token)

        ts = int(time.time() * 1000) % 100000000
        resp = client.post("/api/auth/register", json={
            "phone": f"135{ts:08d}", "password": "test123456", "nickname": "CapTestParent"
        })
        cap_token = resp.json()["token"]
        cap_id = resp.json()["user_id"]

        resp = client.post("/api/auth/children", json={
            "nickname": "CapChild", "age": 7, "gender": "female"
        }, headers={"Authorization": f"Bearer {cap_token}"})
        cap_child_id = resp.json()["child_id"]
        resp = client.post(f"/api/auth/switch-child/{cap_child_id}",
            headers={"Authorization": f"Bearer {cap_token}"})
        cap_child_token = resp.json()["token"]

        from PIL import Image
        img = Image.new("RGB", (50, 50), "red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("cap_art.png", buf, "image/png")},
            data={"title": "Cap Art"},
            headers={"Authorization": f"Bearer {cap_child_token}"},
        )
        cap_work_id = resp.json()["work_id"]

        from core.database import get_db
        with get_db() as conn:
            conn.execute("UPDATE users SET credit_balance = 9999 WHERE id = ?", (cap_id,))

        resp = client.post("/api/merch/order",
            json={"merch_type_id": "postcard", "work_ids": [cap_work_id], "use_credits": 9999},
            headers={"Authorization": f"Bearer {cap_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["credits_used"] == 500  # capped at product price
        assert data["amount_due"] == 0


class TestStubs:
    """认证保护验证"""

    def test_referral_code_requires_auth(self, client):
        resp = client.get("/api/referral/my-code")
        assert resp.status_code == 401

    def test_referral_rewards_requires_auth(self, client):
        resp = client.get("/api/referral/rewards")
        assert resp.status_code == 401


# ============================================================
# 11. 成长档案/展示系统测试
# ============================================================
class TestShowcaseGrowth:
    """成长档案与展示系统"""

    def test_growth_requires_auth(self, client):
        """成长档案需要认证"""
        resp = client.get("/api/showcase/growth")
        assert resp.status_code == 401

    def test_growth_empty(self, client, child_token):
        """新用户成长档案 — 空数据"""
        token, _ = child_token
        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_works"] == 0
        assert data["stats"]["total_tasks"] == 0
        assert data["ability_radar"] is None
        assert data["best_work"] is None
        assert data["recent_works"] == []
        assert data["monthly_works"] == []

    def test_growth_with_works(self, client, child_token):
        """有作品后的成长档案"""
        token, _ = child_token

        # 上传几个作品
        from PIL import Image
        for i, color in enumerate(["red", "green", "blue"]):
            img = Image.new("RGB", (50, 50), color)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            client.post("/api/works/upload",
                files={"image": (f"growth_{i}.png", buf, "image/png")},
                data={"title": f"Growth Art {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_works"] >= 3
        assert len(data["recent_works"]) >= 3
        assert len(data["monthly_works"]) >= 1

    def test_growth_with_evaluation(self, client, child_token, parent_token):
        """评价后的成长档案 — 含能力雷达图"""
        token, _ = child_token

        from PIL import Image
        img = Image.new("RGB", (50, 50), "purple")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        resp = client.post("/api/works/upload",
            files={"image": ("eval_growth.png", buf, "image/png")},
            data={"title": "Evaluated Art"},
            headers={"Authorization": f"Bearer {token}"},
        )
        work_id = resp.json()["work_id"]

        # 家长评价
        client.post(f"/api/works/{work_id}/evaluate",
            json={"originality": 8, "detail": 7, "composition": 9, "expression": 8.5, "feedback": "Great!"},
            headers={"Authorization": f"Bearer {parent_token}"},
        )

        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert data["stats"]["evaluated_works"] >= 1
        assert data["ability_radar"] is not None
        assert data["ability_radar"]["originality"] > 0
        assert data["best_work"] is not None
        assert data["best_work"]["avg_score"] > 0
        assert len(data["eval_trend"]) >= 1

    def test_growth_child_info(self, client, child_token):
        """成长档案包含孩子基本信息"""
        token, _ = child_token
        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "child" in data
        assert "nickname" in data["child"]
        assert "age" in data["child"]
        assert "level_grade" in data["child"]
        assert "joined_at" in data["child"]

    def test_growth_stats_structure(self, client, child_token):
        """成长档案统计结构完整"""
        token, _ = child_token
        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        stats = resp.json()["stats"]
        expected_keys = ["total_works", "total_tasks", "completed_tasks",
                        "in_progress_tasks", "module_a_tasks", "module_b_tasks",
                        "evaluated_works"]
        for key in expected_keys:
            assert key in stats, f"Missing key: {key}"

    def test_growth_monthly_aggregation(self, client, child_token):
        """月度统计正确聚合"""
        token, _ = child_token

        from PIL import Image
        for i in range(3):
            img = Image.new("RGB", (30, 30), "cyan")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            client.post("/api/works/upload",
                files={"image": (f"monthly_{i}.png", buf, "image/png")},
                data={"title": f"Monthly {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        resp = client.get("/api/showcase/growth",
                         headers={"Authorization": f"Bearer {token}"})
        monthly = resp.json()["monthly_works"]
        assert len(monthly) >= 1
        # 当月应有多个作品
        assert monthly[0]["count"] >= 3


# ============================================================
# 12. 健康检查
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


# ============================================================
# 推广裂变系统测试
# ============================================================

class TestReferralSystem:
    """推广系统完整测试"""

    def _register(self, client, phone, invite_code=""):
        """辅助：注册用户"""
        data = {"phone": phone, "password": "test123456", "nickname": f"User{phone[-4:]}"}
        if invite_code:
            data["invite_code"] = invite_code
        resp = client.post("/api/auth/register", json=data)
        assert resp.status_code == 200
        return resp.json()

    def test_get_invite_code(self, client):
        """获取邀请码"""
        u = self._register(client, f"139{int(time.time()*1000)%100000000:08d}")
        resp = client.get("/api/referral/my-code",
                         headers={"Authorization": f"Bearer {u['token']}"})
        assert resp.status_code == 200
        code = resp.json()["invite_code"]
        assert len(code) == 6

    def test_invite_code_stable(self, client):
        """邀请码多次获取应一致"""
        u = self._register(client, f"139{int(time.time()*1000)%100000000:08d}")
        h = {"Authorization": f"Bearer {u['token']}"}
        c1 = client.get("/api/referral/my-code", headers=h).json()["invite_code"]
        c2 = client.get("/api/referral/my-code", headers=h).json()["invite_code"]
        assert c1 == c2

    def test_validate_code_valid(self, client):
        """验证有效邀请码"""
        u = self._register(client, f"139{int(time.time()*1000)%100000000:08d}")
        code = client.get("/api/referral/my-code",
                         headers={"Authorization": f"Bearer {u['token']}"}).json()["invite_code"]
        resp = client.post("/api/referral/validate-code", json={"code": code})
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_validate_code_invalid(self, client):
        """验证无效邀请码"""
        resp = client.post("/api/referral/validate-code", json={"code": "ZZZZZZ"})
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_register_with_invite_code(self, client):
        """带邀请码注册 — L1奖励"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}
        code = client.get("/api/referral/my-code", headers=h_a).json()["invite_code"]

        # B使用A的邀请码注册
        u_b = self._register(client, f"138{ts:08d}", invite_code=code)
        assert "referral" in u_b
        assert u_b["referral"]["applied"] is True

        # A应该有50学币
        dash = client.get("/api/referral/dashboard", headers=h_a).json()
        assert dash["credit_balance"] == 50
        assert dash["total_referrals"] == 1

        # B应该有30学币
        h_b = {"Authorization": f"Bearer {u_b['token']}"}
        bal = client.get("/api/referral/balance", headers=h_b).json()
        assert bal["credit_balance"] == 30

    def test_l2_referral_reward(self, client):
        """二级推荐奖励"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}
        code_a = client.get("/api/referral/my-code", headers=h_a).json()["invite_code"]

        # B用A的码注册
        u_b = self._register(client, f"138{ts:08d}", invite_code=code_a)
        h_b = {"Authorization": f"Bearer {u_b['token']}"}
        code_b = client.get("/api/referral/my-code", headers=h_b).json()["invite_code"]

        # C用B的码注册 → A应获得L2奖励(+10)
        self._register(client, f"137{ts:08d}", invite_code=code_b)

        dash_a = client.get("/api/referral/dashboard", headers=h_a).json()
        assert dash_a["credit_balance"] == 60  # 50(L1) + 10(L2)
        assert dash_a["total_earned"] == 60

    def test_self_referral_blocked(self, client):
        """不能使用自己的邀请码"""
        ts = int(time.time() * 1000) % 100000000
        u = self._register(client, f"139{ts:08d}")
        h = {"Authorization": f"Bearer {u['token']}"}
        code = client.get("/api/referral/my-code", headers=h).json()["invite_code"]

        # 用自己的码再注册一个用户，然后手动测试apply
        from services.referral_service import apply_referral
        result = apply_referral(u["user_id"], code)
        assert result["applied"] is False
        assert "自己" in result["reason"]

    def test_duplicate_referral_blocked(self, client):
        """不能重复绑定邀请人"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}
        code = client.get("/api/referral/my-code", headers=h_a).json()["invite_code"]

        u_b = self._register(client, f"138{ts:08d}", invite_code=code)

        from services.referral_service import apply_referral
        result = apply_referral(u_b["user_id"], code)
        assert result["applied"] is False

    def test_referral_list(self, client):
        """推荐记录列表"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}
        code = client.get("/api/referral/my-code", headers=h_a).json()["invite_code"]

        self._register(client, f"138{ts:08d}", invite_code=code)

        resp = client.get("/api/referral/referrals", headers=h_a)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_reward_history(self, client):
        """学币流水记录"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}
        code = client.get("/api/referral/my-code", headers=h_a).json()["invite_code"]

        self._register(client, f"138{ts:08d}", invite_code=code)

        resp = client.get("/api/referral/rewards", headers=h_a)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert data["items"][0]["amount"] == 50

    def test_dashboard_milestone_tracking(self, client):
        """仪表盘里程碑追踪"""
        ts = int(time.time() * 1000) % 100000000
        u_a = self._register(client, f"139{ts:08d}")
        h_a = {"Authorization": f"Bearer {u_a['token']}"}

        dash = client.get("/api/referral/dashboard", headers=h_a).json()
        assert dash["next_milestone"]["target"] == 5
        assert dash["next_milestone"]["current"] == 0

    def test_referral_requires_auth(self, client):
        """推广接口需要认证"""
        assert client.get("/api/referral/my-code").status_code == 401
        assert client.get("/api/referral/dashboard").status_code == 401
        assert client.get("/api/referral/referrals").status_code == 401
        assert client.get("/api/referral/rewards").status_code == 401
        assert client.get("/api/referral/balance").status_code == 401

    def test_validate_code_no_auth_required(self, client):
        """验证邀请码不需要登录"""
        resp = client.post("/api/referral/validate-code", json={"code": "ABCDEF"})
        assert resp.status_code == 200
