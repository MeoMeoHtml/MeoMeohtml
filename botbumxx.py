"""
╔══════════════════════════════════════════════════════════════╗
║            BUMX TELEGRAM BOT — Multi-User Edition            ║
║  Mỗi user chạy độc lập, không ảnh hưởng nhau                 ║
║  Cấu hình lưu riêng từng user vào data/users/<uid>/          ║
║  TÍCH HỢP KEY SYSTEM (FREE/VIP) — dùng code console gốc      ║
║  Device ID chỉ hiển thị khi nhập key                          ║
╚══════════════════════════════════════════════════════════════╝

CÀI ĐẶT:
    pip install python-telegram-bot==20.7 requests colorama rich --break-system-packages

CHẠY:
    python bumx_bot.py
"""

# ================= PHẦN CODE CONSOLE (GIỮ NGUYÊN) =================
import os
import json
import uuid
import base64
import hashlib
import requests
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.live import Live
from rich.text import Text
from rich import box as rich_box
from rich.style import Style

# Khởi tạo console rich
console = Console()

# ================= CONFIG =================
LINK4M_TOKEN = "654f6dc8fc65186a115a2a4b"
SECRET = "MY_SECRET_2026"

# ĐƯỜNG DẪN VIP SERVER (đã sửa sang nhánh master)
VIP_SERVER = "https://raw.githubusercontent.com/MeoMeoHtml/MeoMeohtml/master/vip_keys.json"
DEVICE_FILE = "device_id.txt"
KEY_FREE_FILE = "key_free.txt"
KEY_VIP_FILE = "key_vip.txt"
# =========================================

# ================= GIAO DIỆN RICH =================
def clear():
    console.clear()

def banner(device_id):
    clear()
    # Banner text
    banner_text = r"""
   _    _      _  ____  ____   ___  _ ____  _    
  / \  / \__/|/ \/ ___\/ ___\  \  \///  _ \/ \ /\
 | |  | |\/||| ||    \|    \   \  / | / \|| | ||
 | |  | |  ||| |\___ |\___ |   / /  | \_/|| \_/|
 \_/  \_/  \|\_/\____/\____/  /_/   \____/\____/
    """
    # Tạo Panel chứa banner và device ID
    banner_panel = Panel(
        Text(banner_text, style="bold red") + 
        Text(f"\n📱 Device ID: {device_id}", style="bold white"),
        title="[bold red]⚡ SYSTEM KEY ⚡[/bold red]",
        subtitle="[bold white]v2.0 (Free 12h)[/bold white]",
        border_style="red",
        box=rich_box.DOUBLE_EDGE,
        padding=(1, 2)
    )
    console.print(banner_panel)

def loading(text="Đang xử lý"):
    with Progress(
        SpinnerColumn(spinner_name="dots", style="red"),
        TextColumn("[bold white]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[red]{text}", total=None)
        time.sleep(1.5)
        progress.update(task, completed=True)
    console.print()

def display_box(title, content, color="red"):
    panel = Panel(
        Text(content, style="bold white"),
        title=f"[bold {color}]{title}[/bold {color}]",
        border_style=color,
        box=rich_box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)

def success_message(msg):
    console.print(f"✅ [bold white]{msg}[/bold white]", style="white")

def error_message(msg):
    console.print(f"❌ [bold red]{msg}[/bold red]", style="red")

def info_message(msg):
    console.print(f"ℹ️ [bold white]{msg}[/bold white]", style="dim white")

def menu_option(key, desc):
    console.print(f"   [bold red]{key}.[/bold red] [white]{desc}[/white]")

# ================= CÁC HÀM XỬ LÝ =================
def encrypt(data):
    return base64.b64encode(data.encode()).decode()

def decrypt(data):
    return base64.b64decode(data.encode()).decode()

def get_device_id():
    if os.path.exists(DEVICE_FILE):
        return decrypt(open(DEVICE_FILE).read().strip())
    device_id = "DV_" + uuid.uuid4().hex[:16]
    open(DEVICE_FILE, "w").write(encrypt(device_id))
    return device_id

def generate_free_key(device_id):
    today = datetime.now().strftime("%Y-%m-%d")
    raw = SECRET + device_id + today
    return hashlib.md5(raw.encode()).hexdigest()[:15]

def save_free_key(device_id, key):
    expire = datetime.now() + timedelta(hours=12)  # 👈 Free 12 giờ
    data = {
        "device": device_id,
        "key": key,
        "expire": expire.isoformat()
    }
    open(KEY_FREE_FILE, "w").write(encrypt(json.dumps(data)))

def check_free_key(device_id):
    if not os.path.exists(KEY_FREE_FILE):
        return False
    try:
        data = json.loads(decrypt(open(KEY_FREE_FILE).read()))
        expire = datetime.fromisoformat(data["expire"])
        if data["device"] == device_id and expire > datetime.now():
            info_message(f"Free còn hạn đến {expire.strftime('%d/%m/%Y %H:%M')}")
            return True
        else:
            os.remove(KEY_FREE_FILE)
            return False
    except:
        os.remove(KEY_FREE_FILE)
        return False

def save_vip_key(device_id, key, days):
    expire = datetime.now() + timedelta(days=days)
    data = {
        "device": device_id,
        "key": key,
        "expire": expire.isoformat()
    }
    open(KEY_VIP_FILE, "w").write(encrypt(json.dumps(data)))

def check_vip_local(device_id):
    if not os.path.exists(KEY_VIP_FILE):
        return False
    try:
        data = json.loads(decrypt(open(KEY_VIP_FILE).read()))
        expire = datetime.fromisoformat(data["expire"])
        if data["device"] == device_id and expire > datetime.now():
            info_message(f"VIP còn hạn đến {expire.strftime('%d/%m/%Y %H:%M')}")
            return True
        else:
            os.remove(KEY_VIP_FILE)
            return False
    except:
        os.remove(KEY_VIP_FILE)
        return False

def check_vip_online(device_id, user_key):
    try:
        url = VIP_SERVER + "?t=" + str(time.time())
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return False, "Không kết nối được server VIP"
        data = res.json()
        vip_list = data.get("vip_keys", [])
        for item in vip_list:
            if item.get("device_id") == device_id:
                if item.get("ten_key") == user_key:
                    days = int(item.get("time", 0))
                    return True, days
                else:
                    return False, "Sai key VIP"
        return False, "Device chưa được cấp VIP"
    except Exception as e:
        return False, f"Lỗi đọc server VIP: {str(e)}"

def create_link4m(url):
    try:
        api = "https://link4m.co/api-shorten/v2"
        params = {
            "api": LINK4M_TOKEN,
            "format": "json",
            "url": url
        }
        res = requests.get(api, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return data.get("shortenedUrl")
        return None
    except:
        return None

# ================= MAIN CONSOLE KEY CHECK (giữ nguyên) =================
def check_key_system():
    device_id = get_device_id()
    banner(device_id)

    # Ưu tiên VIP local
    if check_vip_local(device_id):
        success_message("Truy cập bằng VIP local")
        return True

    # Free còn hạn
    if check_free_key(device_id):
        success_message("Truy cập bằng Free")
        return True

    # Menu lựa chọn
    console.print(Panel(
        "[bold red]CHỌN PHƯƠNG THỨC[/bold red]",
        border_style="red",
        box=rich_box.HEAVY
    ))
    menu_option("1", "🔓 Lấy Key Free (có hạn 12h)")
    menu_option("2", "👑 Nhập Key VIP (dùng lâu dài)")
    console.print()

    choice = console.input("[bold red]👉 Nhập lựa chọn (1 hoặc 2): [/bold red]").strip()

    # ================= FREE =================
    if choice == "1":
        key_today = generate_free_key(device_id)
        random_code = uuid.uuid4().hex[:8]
        web_show_key = f"https://flowing-silo-450510-e1.web.app/?ma={key_today}&r={random_code}"

        loading("⏳ Đang tạo link 4m")
        link = create_link4m(web_show_key)

        if not link:
            error_message("Không tạo được link 4m, vui lòng thử lại sau")
            return False

        display_box("🔗 LINK LẤY KEY FREE", link, color="red")

        while True:
            user_key = console.input("[bold red]🔑 Nhập key từ link trên: [/bold red]").strip()
            if user_key == key_today:
                save_free_key(device_id, user_key)
                expire_time = datetime.now() + timedelta(hours=12)
                success_message(f"Kích hoạt Free thành công! (hết hạn lúc {expire_time.strftime('%d/%m/%Y %H:%M')})")
                return True
            else:
                error_message("Sai key! Vui lòng kiểm tra lại.")

    # ================= VIP =================
    elif choice == "2":
        vip_key = console.input("[bold red]👑 Nhập key VIP: [/bold red]").strip()

        loading("🔎 Đang kiểm tra server VIP")
        ok, result = check_vip_online(device_id, vip_key)

        if ok:
            save_vip_key(device_id, vip_key, result)
            success_message(f"Kích hoạt VIP thành công ({result} ngày)")
            return True
        else:
            error_message(result)
            return False

    else:
        error_message("Lựa chọn không hợp lệ")
        return False

# ================= KẾT THÚC PHẦN CONSOLE =================


# ================= PHẦN BOT TELEGRAM =================
# ─── stdlib ───────────────────────────────────────────────────
import asyncio, random, re, threading
from pathlib import Path
from typing import Optional

# ─── third-party ──────────────────────────────────────────────
from colorama import Fore, init
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters,
)
from telegram.constants import ParseMode

init(autoreset=True)

# ══════════════════════════════════════════════════════════════
#  CẤU HÌNH BOT
# ══════════════════════════════════════════════════════════════
BOT_TOKEN    = "8566293997:AAEhm4e1KQjs99AOLvBQ4pQpWFpz-3ykdp8"   # Lấy từ @BotFather
DATA_DIR     = Path("data/users")       # Thư mục lưu config user
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Danh sách admin (user_id). Để [] = ai cũng dùng được
ADMIN_IDS: list[int] = []

# ══════════════════════════════════════════════════════════════
#  CONVERSATION STATES
# ══════════════════════════════════════════════════════════════
(
    ST_MENU,
    ST_WAIT_AUTH, ST_WAIT_AUTH_PROXY,
    ST_WAIT_COOKIE, ST_WAIT_COOKIE_PROXY, ST_CONFIRM_COOKIE,
    ST_WAIT_TONGJOB, ST_WAIT_DELAY_MIN, ST_WAIT_DELAY_MAX,
    ST_WAIT_API_MIN, ST_WAIT_API_MAX, ST_WAIT_MAX_ERRORS,
    # KEY SYSTEM STATES
    ST_KEY_MENU, ST_WAIT_FREE_KEY, ST_WAIT_VIP_KEY
) = range(15)

# ══════════════════════════════════════════════════════════════
#  LƯU / ĐỌC CONFIG TỪNG USER (giữ nguyên)
# ══════════════════════════════════════════════════════════════
def user_dir(uid: int) -> Path:
    d = DATA_DIR / str(uid)
    d.mkdir(parents=True, exist_ok=True)
    return d

def save_config(uid: int, data: dict):
    p = user_dir(uid) / "config.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config(uid: int) -> dict:
    p = user_dir(uid) / "config.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cookies(uid: int, cookies: list):
    p = user_dir(uid) / "cookies.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)

def load_cookies(uid: int) -> list:
    p = user_dir(uid) / "cookies.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_stats(uid: int, stats: dict):
    p = user_dir(uid) / "stats.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def load_stats(uid: int) -> dict:
    p = user_dir(uid) / "stats.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

# ================= HÀM KIỂM TRA KEY DÙNG CHUNG (gọi console) =================
def is_key_valid() -> bool:
    """Kiểm tra key hiện tại (dùng device_id chung)."""
    dev = get_device_id()
    return check_vip_local(dev) or check_free_key(dev)

# ══════════════════════════════════════════════════════════════
#  TRẠNG THÁI RUNNING (in-memory)
# ══════════════════════════════════════════════════════════════
running_tasks: dict[int, asyncio.Task] = {}
stop_flags: dict[int, threading.Event] = {}

# ══════════════════════════════════════════════════════════════
#  HELPER NETWORK (giữ nguyên)
# ══════════════════════════════════════════════════════════════
def to_requests_proxies(proxy_str: str | None) -> dict | None:
    if not proxy_str:
        return None
    p = proxy_str.strip().split(":")
    if len(p) == 4:
        try:
            host, port, user, pw = p
            int(port)
        except ValueError:
            user, pw, host, port = p
        return {
            "http":  f"http://{user}:{pw}@{host}:{port}",
            "https": f"http://{user}:{pw}@{host}:{port}",
        }
    if len(p) == 2:
        host, port = p
        return {"http": f"http://{host}:{port}", "https": f"http://{host}:{port}"}
    return None

def check_proxy_fast(proxy_str: str) -> bool:
    try:
        r = requests.Session().get(
            "http://www.google.com/generate_204",
            proxies=to_requests_proxies(proxy_str), timeout=6,
        )
        return r.status_code in (204, 200)
    except:
        return False

def encode_to_base64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()

def decode_base64(s: str) -> str:
    return base64.b64decode(s).decode()

def get_id(link: str) -> Optional[str]:
    try:
        r = requests.post(
            "https://id.traodoisub.com/api.php", data={"link": link}, timeout=8
        ).json()
        if r.get("success") == 200:
            return r["id"]
    except:
        pass
    return None

# ══════════════════════════════════════════════════════════════
#  CLASS BUMX (giữ nguyên)
# ══════════════════════════════════════════════════════════════
class BUMX:
    def __init__(self, authorization: str, proxy=None):
        self.proxy = to_requests_proxies(proxy) if proxy and check_proxy_fast(proxy) else None
        self.authorization = authorization
        self.base_url = "https://api-v2.bumx.vn/api"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Dart/3.3 (dart:io)",
            "Content-Type": "application/json",
            "lang": "vi", "version": "37", "origin": "app",
            "authorization": self.authorization,
        }

    def get_wallet_balance(self) -> str:
        try:
            r = self.session.get(
                f"{self.base_url}/business/wallet",
                headers=self.headers, timeout=10, proxies=self.proxy,
            ).json()
            return str(r.get("data", {}).get("balance", r.get("message", "N/A")))
        except Exception as e:
            return f"Lỗi: {e}"

    def connect_account_fb(self, uid):
        try:
            self.session.post(
                "https://api-v2.bumx.vn/api/account-facebook/connect-link",
                headers=self.headers,
                json={"link": f"https://www.facebook.com/profile.php?id={uid}"},
                timeout=10, proxies=self.proxy,
            )
        except:
            pass

    def reload(self, type_job):
        try:
            r = self.session.post(
                "https://api-v2.bumx.vn/api/buff/get-new-mission",
                headers=self.headers, json={"type": type_job},
                timeout=10, proxies=self.proxy,
            ).json()
            if "đã hết nhiệm vụ" in str(r):
                return {"sonv": 0, "cmt": False, "hetnv": True}
            if "Bạn cần làm job comment" in str(r):
                return {"sonv": 0, "cmt": True, "hetnv": False}
            if "Bạn có nhiều nhiệm vụ chưa làm xong" in str(r):
                return {"sonv": 0, "cmt": False, "hetnv": False}
            return {"sonv": len(r.get("data", [])), "cmt": False, "hetnv": False}
        except:
            return {"sonv": 0, "cmt": False, "hetnv": False}

    def get_job_auto(self, type_job):
        res = self.reload(type_job)
        if res.get("cmt"):
            return self.get_job_auto("like_poster")

    def show_job(self):
        try:
            r = self.session.get(
                "https://api-v2.bumx.vn/api/buff/mission",
                headers=self.headers,
                params={"is_from_mobile": "true"},
                timeout=10, proxies=self.proxy,
            ).json()
            if r.get("success") and r.get("count", 0) > 0:
                return r.get("data", [])
        except:
            pass
        return None

    def show_single_job(self, job):
        try:
            r = self.session.post(
                "https://api-v2.bumx.vn/api/buff/load-mission",
                headers=self.headers,
                json={"buff_id": job["buff_id"]},
                timeout=10, proxies=self.proxy,
            ).json()
            if job.get("type") == "like_poster":
                if "Nhiệm vụ này đã đủ số lượng" in str(r):
                    return {"vaild_job": False}
                return {
                    "vaild_job": True, "type_reaction": "",
                    "data": r["data"], "comment_id": r["comment_id"],
                    "link_job": "https://www.facebook.com/" + r["object_id"],
                }
            elif job.get("type") == "like_facebook":
                if "Nhiệm vụ này đã đủ số lượng" in str(r):
                    return {"vaild_job": False}
                icon = r.get("icon", "").lower()
                react = "LIKE"
                for k, v in [("love","LOVE"),("thuongthuong","LOVE"),("care","CARE"),
                              ("wow","WOW"),("sad","SAD"),("angry","ANGRY"),("haha","HAHA")]:
                    if k in icon:
                        react = v; break
                return {
                    "vaild_job": True,
                    "link_job": "https://www.facebook.com/" + r["object_id"],
                    "type_reaction": react, "data": "", "comment_id": "",
                }
        except:
            pass
        return {"vaild_job": False, "type_reaction": "", "data": "", "comment_id": "", "link_job": ""}

    def format_json_job(self, job, res):
        return {
            "vaild_job": res.get("vaild_job"),
            "comment_msg": res.get("data"),
            "comment_id": res.get("comment_id"),
            "link_job": res.get("link_job"),
            "buff_id": job.get("buff_id"),
            "type_job": job.get("type"),
            "type_reaction": res.get("type_reaction"),
        }

    def skip_job(self, job):
        buff_id = job.get("buff_id") if isinstance(job, dict) else None
        if not buff_id:
            return
        try:
            self.session.post(
                f"{self.base_url}/buff/report-buff",
                headers=self.headers, json={"buff_id": buff_id},
                timeout=10, proxies=self.proxy,
            )
        except:
            pass

    def submit_job(self, json_job, link_share=""):
        try:
            data = {
                "buff_id": json_job["buff_id"],
                "comment": None, "comment_id": None,
                "code_submit": None, "attachments": [],
                "link_share": "", "code": "",
                "is_from_mobile": True,
                "type": json_job["type_job"],
                "sub_id": None, "data": None,
            }
            if json_job["type_job"] == "like_facebook":
                data["comment"] = "tt nha"
            elif json_job["type_job"] == "like_poster":
                data["comment"] = json_job.get("data")
                data["comment_id"] = json_job.get("comment_id")
            elif json_job["type_job"] == "review_facebook":
                data["comment"] = "Helo Bạn chúc Bạn sức khỏe"
                data["link_share"] = link_share
            return self.session.post(
                "https://api-v2.bumx.vn/api/buff/submit-mission",
                headers=self.headers, json=data,
                timeout=10, proxies=self.proxy,
            ).json()
        except:
            return None

# ══════════════════════════════════════════════════════════════
#  CLASS FB (giữ nguyên)
# ══════════════════════════════════════════════════════════════
class FB:
    def __init__(self, cookie, proxy=None):
        self.cookie = cookie
        self.proxy = to_requests_proxies(proxy) if proxy and check_proxy_fast(proxy) else None
        self.session = requests.Session()
        self.s = self.session
        self.user_id = None
        self.lsd = self.fb_dtsg = self.jazoest = self.session_id = self.headers = None
        try:
            self.user_id = cookie.split("c_user=")[1].split(";")[0]
            headers_get = {
                "authority": "www.facebook.com",
                "accept": "text/html,application/xhtml+xml",
                "accept-language": "vi",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cookie": cookie,
            }
            url = self.s.get(f"https://www.facebook.com/{self.user_id}",
                             headers=headers_get, proxies=self.proxy).url
            resp = requests.get(url, headers=headers_get, proxies=self.proxy).text
            self.lsd       = re.findall(r'"LSD",\[],{"token":".*?"', resp)[0].split('":"')[1].split('"')[0]
            self.fb_dtsg   = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', resp)[0]
            self.jazoest   = re.findall(r'&jazoest=.*?"', resp)[0].split("=")[1].split('"')[0]
            self.session_id= re.findall(r'"profile_session_id":".*?"', resp)[0].split('":"')[1].split('"')[0]
            self.headers = {
                "accept": "*/*", "accept-language": "vi-VN,vi;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://www.facebook.com",
                "referer": "https://www.facebook.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "x-fb-lsd": self.lsd, "cookie": cookie,
            }
        except:
            self.user_id = None

    def react(self, id_job, type_react, id_profile=None):
        try:
            if not id_profile:
                id_profile = self.user_id
            reac = {"LIKE":"1635855486666999","LOVE":"1678524932434102","CARE":"613557422527858",
                    "HAHA":"115940658764963","WOW":"478547315650144","SAD":"908563459236466","ANGRY":"444813342392137"}
            id_react = reac.get(type_react.upper(), reac["LIKE"])
            data = {
                "av": str(id_profile), "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest, "lsd": self.lsd,
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "CometUFIFeedbackReactMutation",
                "server_timestamps": "true",
                "variables": json.dumps({
                    "input": {
                        "feedback_id": encode_to_base64(f"feedback:{id_job}"),
                        "feedback_reaction_id": id_react,
                        "feedback_source": "MEDIA_VIEWER",
                        "is_tracking_encrypted": True, "tracking": [],
                        "session_id": self.session_id,
                        "actor_id": str(id_profile),
                        "client_mutation_id": "2",
                    }, "useDefaultActor": False,
                }), "doc_id": "24198888476452283",
            }
            r = self.s.post("https://www.facebook.com/api/graphql/",
                            headers=self.headers, data=data, proxies=self.proxy)
            return "viewer_feedback_reaction_info" in r.text
        except:
            return False

    def comment(self, id_job, msg, id_profile=None):
        try:
            if not id_profile:
                id_profile = self.user_id
            data = {
                "av": id_profile, "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest, "lsd": self.lsd,
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "useCometUFICreateCommentMutation",
                "server_timestamps": "true",
                "variables": json.dumps({
                    "input": {
                        "actor_id": str(id_profile),
                        "feedback_id": encode_to_base64(f"feedback:{id_job}"),
                        "message": {"ranges": [], "text": msg},
                        "session_id": self.session_id,
                        "idempotence_token": f"client:{uuid.uuid4()}",
                    },
                }), "doc_id": "25082280574724522",
            }
            r = self.s.post("https://www.facebook.com/api/graphql/",
                            headers=self.headers, data=data, proxies=self.proxy)
            return True
        except:
            return False

    def check_cookie(self) -> bool:
        try:
            r = self.session.get("https://www.facebook.com/",
                                 headers=self.headers, proxies=self.proxy)
            for sig in ["601051028565049","1501092823525282","828281030927956",
                        'title="Log in to Facebook">']:
                if sig in r.text:
                    return False
            return True
        except:
            return False

def LAMJOB(fb: FB, json_job: dict) -> bool:
    try:
        id_job = get_id(json_job.get("link_job", ""))
        if not id_job:
            return False
        if json_job.get("type_job") == "like_facebook":
            return fb.react(id_job, json_job.get("type_reaction", "LIKE"))
        elif json_job.get("type_job") == "like_poster":
            return fb.comment(id_job, json_job.get("comment_msg", ""))
    except:
        return False
    return False

# ══════════════════════════════════════════════════════════════
#  WORKER — chạy trong thread riêng cho mỗi user (giữ nguyên)
# ══════════════════════════════════════════════════════════════
async def worker(uid: int, app: Application):
    """Chạy tool BUMX cho 1 user, gửi log lên Telegram."""
    cfg      = load_config(uid)
    cookies  = load_cookies(uid)
    stop_ev  = stop_flags.get(uid, threading.Event())

    async def send(msg: str):
        try:
            await app.bot.send_message(chat_id=uid, text=msg, parse_mode=ParseMode.HTML)
        except:
            pass

    bumx = BUMX(cfg["authorization"], cfg.get("proxy_bumx", ""))

    try:
        balance = bumx.get_wallet_balance()
    except:
        await send("❌ Token lỗi hoặc không kết nối được BUMX")
        return

    TONGJOB     = int(cfg.get("tongjob", 10))
    delay_min   = int(cfg.get("delay_min", 5))
    delay_max   = int(cfg.get("delay_max", 15))
    api_min     = int(cfg.get("api_min", 2))
    api_max     = int(cfg.get("api_max", 5))
    MAX_ERRORS  = int(cfg.get("max_errors", 5))

    stats = {
        "balance":      balance,
        "task":         "BUMX",
        "cookie_total": len(cookies),
        "change_acc":   TONGJOB,
        "earned":       0,
        "job_done":     0,
        "cookie_live":  len(cookies),
        "proxy":        1 if cfg.get("proxy_bumx") else 0,
        "delay":        f"{delay_min}-{delay_max}s",
        "cookie_block": 0,
        "job_block":    0,
        "cycle":        1,
        "user":         cfg.get("username", str(uid)),
        "started_at":   datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
    }
    save_stats(uid, stats)

    def fmt_stats() -> str:
        return (
            f"📊 <b>TRẠNG THÁI TOOL</b>\n"
            f"├ 💰 Số dư: <code>{stats['balance']}</code>\n"
            f"├ 🍪 Cookie: {stats['cookie_live']}/{stats['cookie_total']} live\n"
            f"├ ✅ Job done: <b>{stats['job_done']}</b> | 💵 Đã kiếm: <b>{stats['earned']}₫</b>\n"
            f"├ ❌ Cookie block: {stats['cookie_block']} | Job block: {stats['job_block']}\n"
            f"├ 🔄 Đổi acc sau: {stats['change_acc']} job\n"
            f"└ ⏰ Delay: {stats['delay']}"
        )

    await send(f"🚀 <b>BẮT ĐẦU CHẠY TOOL BUMX</b>\n{fmt_stats()}")

    loop = asyncio.get_event_loop()

    def job_type_label(json_job: dict) -> str:
        type_job   = json_job.get("type_job", "")
        react_type = json_job.get("type_reaction", "")
        if type_job == "like_facebook":
            icons = {"LIKE":"👍","LOVE":"❤️","CARE":"🤗","HAHA":"😂","WOW":"😮","SAD":"😢","ANGRY":"😡"}
            return f"{icons.get(react_type, '👍')} Like Facebook ({react_type})"
        elif type_job == "like_poster":
            return "💬 Comment bài viết"
        elif type_job == "review_facebook":
            return "⭐ Review Facebook"
        return f"📌 {type_job}"

    async def auto_reload(type_job="like_facebook"):
        res = await loop.run_in_executor(None, lambda: bumx.reload(type_job))
        if res.get("cmt"):
            await send("ℹ️ Server yêu cầu làm job comment trước...")
            await loop.run_in_executor(None, lambda: bumx.reload("like_poster"))
        elif res.get("hetnv"):
            await send(f"⏳ Hết nhiệm vụ <b>{type_job}</b> — đợi 60s rồi thử lại...")
            await asyncio.sleep(60)
            await auto_reload(type_job)
        else:
            sonv_moi = res.get("sonv", 0)
            if sonv_moi > 0:
                await send(f"📥 Đã tải <b>{sonv_moi}</b> nhiệm vụ mới từ server")

    consecutive_errors = 0

    for idx_acc, data_fb in enumerate(cookies, 1):
        if stop_ev.is_set():
            break

        cookie_fb = data_fb["cookie"]
        proxy_fb  = data_fb.get("proxy", "")
        sonv      = 0

        await send(f"🔑 <b>Đang khởi tạo ACC {idx_acc}/{len(cookies)}...</b>")

        _ck  = cookie_fb
        _px  = proxy_fb
        fb   = await loop.run_in_executor(None, lambda: FB(_ck, _px))

        if not fb.user_id:
            stats["cookie_block"] += 1
            save_stats(uid, stats)
            await send(f"⚠️ <b>Cookie {idx_acc} lỗi</b> — bỏ qua, sang acc tiếp theo")
            continue

        await send(f"✅ Login thành công | UID: <code>{fb.user_id}</code>")

        _uid_fb = fb.user_id
        await loop.run_in_executor(None, lambda: bumx.connect_account_fb(_uid_fb))

        await auto_reload("like_facebook")

        no_job_count = 0

        while sonv < TONGJOB:
            if stop_ev.is_set():
                break

            cookie_ok = await loop.run_in_executor(None, fb.check_cookie)
            if not cookie_ok:
                stats["cookie_live"] -= 1
                save_stats(uid, stats)
                await send(f"💀 <b>Cookie die</b> — đổi sang acc tiếp theo\n{fmt_stats()}")
                break

            all_jobs = await loop.run_in_executor(None, bumx.show_job)

            if not all_jobs:
                no_job_count += 1
                if no_job_count >= 3:
                    await send("🔄 Queue trống — đang xin job mới từ server...")
                    await auto_reload("like_facebook")
                    no_job_count = 0
                    await asyncio.sleep(random.randint(api_min, api_max))
                else:
                    await asyncio.sleep(10)
                continue

            no_job_count = 0

            for job in all_jobs:
                if stop_ev.is_set() or sonv >= TONGJOB:
                    break

                _job = job

                res_load = await loop.run_in_executor(
                    None, lambda: bumx.show_single_job(_job)
                )

                if not isinstance(res_load, dict) or not res_load.get("vaild_job"):
                    await loop.run_in_executor(None, lambda: bumx.skip_job(_job))
                    stats["job_block"] += 1
                    save_stats(uid, stats)
                    consecutive_errors += 1
                    if consecutive_errors >= MAX_ERRORS:
                        await send(f"⛔ Đã đạt <b>{MAX_ERRORS}</b> lỗi liên tiếp. Dừng tool.")
                        stop_ev.set()
                        break
                    continue

                json_job  = bumx.format_json_job(_job, res_load)
                _jj       = json_job

                delay_fb  = random.randint(delay_min, delay_max)
                start_t   = time.time()

                success = await loop.run_in_executor(None, lambda: LAMJOB(fb, _jj))

                if success:
                    _jj2 = _jj
                    res_submit = await loop.run_in_executor(
                        None, lambda: bumx.submit_job(_jj2)
                    )

                    tien_nhan = 0
                    if isinstance(res_submit, dict):
                        d = res_submit.get("data", {}) or {}
                        tien_nhan = (
                            d.get("price")
                            or d.get("coin")
                            or d.get("amount")
                            or d.get("reward")
                            or 0
                        )
                        if not tien_nhan:
                            type_job_now = _jj2.get("type_job", "")
                            if type_job_now == "like_facebook":
                                tien_nhan = 20
                            elif type_job_now == "like_poster":
                                tien_nhan = 50
                            elif type_job_now == "review_facebook":
                                tien_nhan = 50
                            else:
                                tien_nhan = 20
                    else:
                        type_job_now = _jj2.get("type_job", "")
                        tien_nhan = 50 if type_job_now in ("like_poster", "review_facebook") else 20

                    sonv              += 1
                    stats["job_done"] += 1
                    stats["earned"]   += tien_nhan
                    save_stats(uid, stats)

                    consecutive_errors = 0

                    label = job_type_label(_jj2)
                    await send(
                        f"✅ <b>Job {stats['job_done']}</b> thành công!\n"
                        f"├ 📋 Loại: {label}\n"
                        f"├ 💰 Job này: <b>+{tien_nhan}₫</b>\n"
                        f"├ 🔄 ACC {sonv}/{TONGJOB}\n"
                        f"└ 💵 Tổng kiếm: <b>{stats['earned']}₫</b>"
                    )

                    await loop.run_in_executor(
                        None, lambda: bumx.get_job_auto("like_facebook")
                    )

                    await asyncio.sleep(random.randint(api_min, api_max))

                    remain = max(0, delay_fb - (time.time() - start_t))
                    if remain > 0:
                        await asyncio.sleep(remain)

                else:
                    stats["job_block"] += 1
                    save_stats(uid, stats)
                    await loop.run_in_executor(None, lambda: bumx.skip_job(_jj))
                    consecutive_errors += 1
                    if consecutive_errors >= MAX_ERRORS:
                        await send(f"⛔ Đã đạt <b>{MAX_ERRORS}</b> lỗi liên tiếp. Dừng tool.")
                        stop_ev.set()
                        break

            if stop_ev.is_set():
                break

        if stop_ev.is_set():
            break

        await send(
            f"🔚 <b>Xong ACC {idx_acc}</b> | Đã làm <b>{sonv}</b> job\n"
            f"Chuyển sang acc tiếp theo..."
        )

    save_stats(uid, stats)
    await send(
        f"🏁 <b>HOÀN THÀNH TOOL</b>\n\n"
        f"📊 <b>Tổng kết:</b>\n"
        f"├ ✅ Tổng job: <b>{stats['job_done']}</b>\n"
        f"├ 💵 Tổng kiếm: <b>{stats['earned']}₫</b>\n"
        f"├ 🍪 Cookie live: {stats['cookie_live']}/{stats['cookie_total']}\n"
        f"├ ❌ Cookie block: {stats['cookie_block']}\n"
        f"└ ⛔ Job block: {stats['job_block']}"
    )
    running_tasks.pop(uid, None)
    stop_flags.pop(uid, None)

# ══════════════════════════════════════════════════════════════
#  KEYBOARDS (đã loại bỏ nút key khỏi menu chính và nút Device ID khỏi menu key)
# ══════════════════════════════════════════════════════════════
def main_keyboard(with_key=True):
    """
    Trả về keyboard.
    - with_key=False: menu dành cho người chưa có key (chỉ hiển thị các nút key + trợ giúp).
    - with_key=True: menu chính dành cho người đã có key (không hiển thị nút key).
    """
    if not with_key:
        return ReplyKeyboardMarkup([
            ["🔑 Kích hoạt Key Free", "👑 Nhập Key VIP"],
            ["❓ Trợ giúp"]
        ], resize_keyboard=True)
    # Menu chính (đã có key) – không bao gồm các nút key
    return ReplyKeyboardMarkup([
        ["⚙️ Cấu hình Auth BUMX", "🍪 Quản lý Cookie"],
        ["🛠 Cài đặt chạy",        "📋 Xem cấu hình"],
        ["▶️ Bắt đầu chạy",       "⏹ Dừng tool"],
        ["📊 Xem thống kê",        "❓ Trợ giúp"],
        ["🚀 Mua VPS Giá rẻ",      "📞 Liên hệ Admin"],
    ], resize_keyboard=True)

# ══════════════════════════════════════════════════════════════
#  HANDLERS
# ══════════════════════════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name

    if is_key_valid():
        cfg  = load_config(uid)
        text = (
            f"👋 Xin chào <b>{name}</b>!\n\n"
            f"🤖 <b>BUMX Bot</b> — Tool kiếm tiền tự động\n\n"
            f"{'✅ Đã có cấu hình. Nhấn ▶️ để bắt đầu!' if cfg.get('authorization') else '⚠️ Chưa cấu hình. Nhấn ⚙️ để thiết lập.'}\n\n"
            f"👑 <b>THÔNG TIN ADMIN</b>\n"
            f"• Lê Tuấn - @Bomaylatop1\n"
            f"• Alex - @Dacvumeomeo19\n"
            f"©️ Bản quyền thuộc về Lê Tuấn và Alex\n\n"
            f"🚀 <b>Cần VPS giá rẻ?</b> Ghé ngay: http://bvzone.cloud/aff.php?aff=158"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True))
        return ST_MENU
    else:
        await update.message.reply_text(
            f"🔐 <b>BẠN CHƯA CÓ KEY HOẶC KEY ĐÃ HẾT HẠN</b>\n\n"
            f"Vui lòng kích hoạt key để sử dụng bot.\n\n"
            f"• <b>Key Free</b>: có hiệu lực 12 giờ, được tạo tự động.\n"
            f"• <b>Key VIP</b>: mua từ admin, dùng lâu dài.\n\n"
            f"Chọn một trong các mục bên dưới:",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(False)
        )
        return ST_KEY_MENU

# ─── KEY MENU HANDLERS ────────────────────────────────────────
async def handle_key_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    device_id = get_device_id()

    if "Kích hoạt Key Free" in text:
        # Hiển thị device ID trước
        await update.message.reply_text(
            f"📱 <b>Device ID của bạn:</b> <code>{device_id}</code>\n\n"
            f"Đang tạo key free...",
            parse_mode=ParseMode.HTML
        )
        key = generate_free_key(device_id)
        random_code = uuid.uuid4().hex[:8]
        web_url = f"https://flowing-silo-450510-e1.web.app/?ma={key}&r={random_code}"
        link = create_link4m(web_url)
        if link:
            await update.message.reply_text(
                f"🔗 <b>LINK LẤY KEY FREE CỦA BẠN</b>\n\n"
                f"{link}\n\n"
                f"👉 Nhấn vào link, copy key và gửi lại cho bot.\n"
                f"(Gõ /cancel để hủy)",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"🔑 <b>KEY FREE CỦA BẠN</b>\n\n"
                f"<code>{key}</code>\n\n"
                f"Vui lòng copy key và gửi lại cho bot.\n"
                f"(Gõ /cancel để hủy)",
                parse_mode=ParseMode.HTML
            )
        ctx.user_data["expected_free_key"] = key
        return ST_WAIT_FREE_KEY

    elif "Nhập Key VIP" in text:
        await update.message.reply_text(
            f"📱 <b>Device ID của bạn:</b> <code>{device_id}</code>\n\n"
            f"👑 Vui lòng nhập <b>key VIP</b> của bạn:\n"
            f"(Gõ /cancel để hủy)",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return ST_WAIT_VIP_KEY

    elif "Trợ giúp" in text:
        await update.message.reply_text(
            "❓ <b>HƯỚNG DẪN KÍCH HOẠT KEY</b>\n\n"
            "<b>Key Free:</b>\n"
            "• Bot sẽ tạo key và gửi link 4m.\n"
            "• Bạn nhấn link, copy key và gửi lại.\n"
            "• Key có hiệu lực 12 giờ.\n\n"
            "<b>Key VIP:</b>\n"
            "• Liên hệ admin @Bomaylatop1 hoặc @Dacvumeomeo19 để mua.\n"
            "• Nhập key VIP vào ô tương ứng.\n\n"
            "<b>Lưu ý:</b> Device ID của bạn sẽ hiển thị khi bạn chọn một trong hai hình thức nhập key.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(False)
        )
        return ST_KEY_MENU

    return ST_KEY_MENU

async def recv_free_key(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    device_id = get_device_id()
    user_key = update.message.text.strip()
    expected = ctx.user_data.get("expected_free_key")

    if user_key == expected:
        save_free_key(device_id, user_key)
        expire = datetime.now() + timedelta(hours=12)
        await update.message.reply_text(
            f"✅ <b>Kích hoạt Key Free thành công!</b>\n"
            f"⏳ Hết hạn lúc: {expire.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Bạn có thể sử dụng bot ngay bây giờ.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(True)
        )
        ctx.user_data.pop("expected_free_key", None)
        return ST_MENU
    else:
        await update.message.reply_text(
            "❌ <b>Key không đúng!</b> Vui lòng kiểm tra lại hoặc yêu cầu key mới.\n"
            "(Gõ /cancel để hủy)",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return ST_WAIT_FREE_KEY

async def recv_vip_key(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    device_id = get_device_id()
    vip_key = update.message.text.strip()

    ok, result = check_vip_online(device_id, vip_key)
    if ok:
        save_vip_key(device_id, vip_key, result)
        expire = datetime.now() + timedelta(days=result)
        await update.message.reply_text(
            f"✅ <b>Kích hoạt Key VIP thành công!</b>\n"
            f"⏳ Hết hạn lúc: {expire.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Chúc bạn dùng bot vui vẻ!",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(True)
        )
        return ST_MENU
    else:
        await update.message.reply_text(
            f"❌ <b>Key không hợp lệ!</b>\n\nLý do: {result}\n\n"
            f"Vui lòng kiểm tra lại hoặc liên hệ admin.\n"
            f"(Gõ /cancel để hủy)",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return ST_WAIT_VIP_KEY

# ─── CÁC HANDLER KHÁC (giữ nguyên) ───────────────────────────
async def menu_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    cfg = load_config(uid)
    existing = f"\n📌 Auth hiện tại: <code>{cfg['authorization'][:30]}...</code>" if cfg.get("authorization") else ""
    await update.message.reply_text(
        f"🔑 <b>Cấu hình Authorization BUMX</b>{existing}\n\n"
        "Nhập <b>authorization</b> của bạn (lấy trong app BUMX → Profile → Token):\n"
        "(Gõ /cancel để huỷ)",
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove(),
    )
    return ST_WAIT_AUTH

async def recv_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["new_auth"] = update.message.text.strip()
    await update.message.reply_text(
        "🌐 Nhập <b>proxy cho tài khoản BUMX</b> (dạng host:port hoặc user:pass:host:port).\n"
        "Gõ <code>-</code> nếu không dùng proxy:",
        parse_mode=ParseMode.HTML,
    )
    return ST_WAIT_AUTH_PROXY

async def recv_auth_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    proxy = update.message.text.strip()
    if proxy == "-":
        proxy = ""

    cfg = load_config(uid)
    cfg["authorization"] = ctx.user_data.pop("new_auth")
    cfg["proxy_bumx"]    = proxy

    try:
        bumx = BUMX(cfg["authorization"], proxy)
        balance = bumx.get_wallet_balance()
        cfg["username"] = f"BUMX_USER_{uid}"
        cfg["balance"]  = balance
        msg = f"✅ <b>Lưu auth thành công!</b>\n💰 Số dư: <b>{balance}</b>"
    except:
        msg = "✅ Đã lưu auth (chưa kiểm tra kết nối)"

    if not cfg.get("tongjob"):
        cfg["tongjob"]   = 10
        cfg["delay_min"] = 5
        cfg["delay_max"] = 15
        cfg["api_min"]   = 2
        cfg["api_max"]   = 5
        cfg["max_errors"] = 5

    save_config(uid, cfg)
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True))
    return ST_MENU

async def menu_cookie(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    cookies = load_cookies(uid)
    info    = f"📦 Hiện có <b>{len(cookies)}</b> cookie\n\n" if cookies else "📭 Chưa có cookie nào\n\n"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Thêm cookie mới",   callback_data="ck_add")],
        [InlineKeyboardButton("🗑 Xoá tất cả cookie", callback_data="ck_clear")],
        [InlineKeyboardButton("📋 Xem danh sách",     callback_data="ck_list")],
        [InlineKeyboardButton("🔙 Quay lại",          callback_data="ck_back")],
    ])
    await update.message.reply_text(
        f"🍪 <b>Quản lý Cookie Facebook</b>\n{info}Chọn thao tác:",
        parse_mode=ParseMode.HTML, reply_markup=kb,
    )
    return ST_MENU

async def cb_cookie(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = q.from_user.id
    await q.answer()
    act = q.data

    if act == "ck_add":
        await q.message.reply_text(
            "🍪 Nhập <b>cookie Facebook</b> (dạng đầy đủ, có c_user=...):\n(Gõ /cancel để huỷ)",
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove(),
        )
        return ST_WAIT_COOKIE

    elif act == "ck_clear":
        save_cookies(uid, [])
        await q.edit_message_text("🗑 Đã xoá tất cả cookie!")
        return ST_MENU

    elif act == "ck_list":
        cookies = load_cookies(uid)
        if not cookies:
            await q.edit_message_text("📭 Không có cookie nào.")
            return ST_MENU
        lines = []
        for i, c in enumerate(cookies, 1):
            uid_fb = "N/A"
            if "c_user=" in c["cookie"]:
                uid_fb = c["cookie"].split("c_user=")[1].split(";")[0]
            proxy_info = f" | proxy: {c['proxy'][:20]}..." if c.get("proxy") else " | no proxy"
            lines.append(f"{i}. UID: <code>{uid_fb}</code>{proxy_info}")
        await q.edit_message_text(
            "📋 <b>Danh sách cookie:</b>\n" + "\n".join(lines),
            parse_mode=ParseMode.HTML,
        )
        return ST_MENU

    elif act == "ck_back":
        await q.edit_message_text("🏠 Quay lại menu chính")
        await q.message.reply_text("Menu chính:", reply_markup=main_keyboard(True))
        return ST_MENU

    return ST_MENU

async def recv_cookie(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["new_cookie"] = update.message.text.strip()
    await update.message.reply_text(
        "🌐 Nhập <b>proxy cho cookie này</b> (host:port hoặc user:pass:host:port).\n"
        "Gõ <code>-</code> nếu không dùng:",
        parse_mode=ParseMode.HTML,
    )
    return ST_WAIT_COOKIE_PROXY

async def recv_cookie_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    proxy  = update.message.text.strip()
    if proxy == "-":
        proxy = ""
    cookie = ctx.user_data.pop("new_cookie", "")

    if "c_user=" not in cookie:
        await update.message.reply_text(
            "❌ Cookie không hợp lệ (thiếu c_user=). Thử lại:",
            reply_markup=main_keyboard(True),
        )
        return ST_MENU

    cookies = load_cookies(uid)
    cookies.append({"cookie": cookie, "proxy": proxy,
                    "added_at": datetime.now().strftime("%d/%m/%Y %H:%M")})
    save_cookies(uid, cookies)

    fb_uid = cookie.split("c_user=")[1].split(";")[0]
    await update.message.reply_text(
        f"✅ Đã thêm cookie!\n"
        f"👤 UID Facebook: <code>{fb_uid}</code>\n"
        f"📦 Tổng cookie: <b>{len(cookies)}</b>",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def menu_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    cfg = load_config(uid)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Chỉnh sửa cấu hình", callback_data="cfg_edit")],
        [InlineKeyboardButton("🔙 Quay lại",            callback_data="cfg_back")],
    ])
    await update.message.reply_text(
        "🛠 <b>CÀI ĐẶT CHẠY TOOL</b>\n\n"
        f"├ 🔄 Job rồi nghỉ (đổi acc): <b>{cfg.get('tongjob', 10)}</b>\n"
        f"├ ⏱ Delay min: <b>{cfg.get('delay_min', 5)}s</b>\n"
        f"├ ⏱ Delay max: <b>{cfg.get('delay_max', 15)}s</b>\n"
        f"├ 🔌 API delay min: <b>{cfg.get('api_min', 2)}s</b>\n"
        f"├ 🔌 API delay max: <b>{cfg.get('api_max', 5)}s</b>\n"
        f"└ ⚠️ Lỗi liên tiếp tối đa: <b>{cfg.get('max_errors', 5)}</b>\n\n"
        "Nhấn <b>Chỉnh sửa</b> để thay đổi:",
        parse_mode=ParseMode.HTML, reply_markup=kb,
    )
    return ST_MENU

async def cb_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = q.from_user.id
    await q.answer()

    if q.data == "cfg_edit":
        await q.message.reply_text(
            "📝 <b>Nhập số job làm rồi nghỉ/đổi acc:</b>\n"
            "Ví dụ: <code>10</code>",
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove(),
        )
        return ST_WAIT_TONGJOB

    elif q.data == "cfg_back":
        await q.edit_message_text("🏠 Quay lại menu chính")
        await q.message.reply_text("Menu chính:", reply_markup=main_keyboard(True))
        return ST_MENU

    return ST_MENU

async def recv_tongjob(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        if v <= 0: raise ValueError
        ctx.user_data["tongjob"] = v
        await update.message.reply_text(
            f"✅ Job / lần: <b>{v}</b>\n\n"
            "⏱ <b>[2/6] Nhập Delay MIN</b> (giây, giữa các job):\n"
            "Ví dụ: <code>5</code>",
            parse_mode=ParseMode.HTML,
        )
        return ST_WAIT_DELAY_MIN
    except:
        await update.message.reply_text("❌ Nhập số nguyên dương (vd: <code>10</code>):", parse_mode=ParseMode.HTML)
        return ST_WAIT_TONGJOB

async def recv_delay_min(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        if v < 0: raise ValueError
        ctx.user_data["delay_min"] = v
        await update.message.reply_text(
            f"✅ Delay min: <b>{v}s</b>\n\n"
            "⏱ <b>[3/6] Nhập Delay MAX</b> (giây, phải >= delay min):\n"
            "Ví dụ: <code>15</code>",
            parse_mode=ParseMode.HTML,
        )
        return ST_WAIT_DELAY_MAX
    except:
        await update.message.reply_text("❌ Nhập số nguyên >= 0:", parse_mode=ParseMode.HTML)
        return ST_WAIT_DELAY_MIN

async def recv_delay_max(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        if v < ctx.user_data.get("delay_min", 0): raise ValueError
        ctx.user_data["delay_max"] = v
        await update.message.reply_text(
            f"✅ Delay max: <b>{v}s</b>\n\n"
            "🔌 <b>[4/6] Nhập API Delay MIN</b> (giây, delay sau khi lấy job):\n"
            "Ví dụ: <code>2</code>",
            parse_mode=ParseMode.HTML,
        )
        return ST_WAIT_API_MIN
    except:
        dmin = ctx.user_data.get("delay_min", 0)
        await update.message.reply_text(f"❌ Phải >= delay min ({dmin}s):", parse_mode=ParseMode.HTML)
        return ST_WAIT_DELAY_MAX

async def recv_api_min(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        if v < 0: raise ValueError
        ctx.user_data["api_min"] = v
        await update.message.reply_text(
            f"✅ API delay min: <b>{v}s</b>\n\n"
            "🔌 <b>[5/6] Nhập API Delay MAX</b> (giây, phải >= api delay min):\n"
            "Ví dụ: <code>5</code>",
            parse_mode=ParseMode.HTML,
        )
        return ST_WAIT_API_MAX
    except:
        await update.message.reply_text("❌ Nhập số nguyên >= 0:", parse_mode=ParseMode.HTML)
        return ST_WAIT_API_MIN

async def recv_api_max(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        if v < ctx.user_data.get("api_min", 0): raise ValueError
        ctx.user_data["api_max"] = v
        await update.message.reply_text(
            f"✅ API delay max: <b>{v}s</b>\n\n"
            "⚠️ <b>[6/6] Nhập số lỗi liên tiếp tối đa</b> (nếu vượt quá sẽ dừng bot):\n"
            "Ví dụ: <code>5</code>",
            parse_mode=ParseMode.HTML,
        )
        return ST_WAIT_MAX_ERRORS
    except:
        amin = ctx.user_data.get("api_min", 0)
        await update.message.reply_text(f"❌ Phải >= api delay min ({amin}s):", parse_mode=ParseMode.HTML)
        return ST_WAIT_API_MAX

async def recv_max_errors(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        v = int(update.message.text.strip())
        if v <= 0: raise ValueError
        ctx.user_data["max_errors"] = v
    except:
        await update.message.reply_text("❌ Nhập số nguyên dương (vd: 5):", parse_mode=ParseMode.HTML)
        return ST_WAIT_MAX_ERRORS

    cfg = load_config(uid)
    for k in ("tongjob","delay_min","delay_max","api_min","api_max","max_errors"):
        cfg[k] = ctx.user_data.pop(k, cfg.get(k))
    save_config(uid, cfg)

    await update.message.reply_text(
        f"✅ <b>Đã lưu cấu hình!</b>\n\n"
        f"├ 🔄 Job rồi nghỉ (đổi acc): <b>{cfg['tongjob']}</b>\n"
        f"├ ⏱ Delay job: <b>{cfg['delay_min']} – {cfg['delay_max']}s</b>\n"
        f"├ 🔌 API delay: <b>{cfg['api_min']} – {cfg['api_max']}s</b>\n"
        f"└ ⚠️ Lỗi liên tiếp tối đa: <b>{cfg['max_errors']}</b>",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def cmd_run(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    cfg     = load_config(uid)
    cookies = load_cookies(uid)

    if uid in running_tasks and not running_tasks[uid].done():
        await update.message.reply_text("⚠️ Tool đang chạy rồi! Dừng trước khi chạy lại.")
        return ST_MENU

    if not cfg.get("authorization"):
        await update.message.reply_text("❌ Chưa cấu hình Authorization. Nhấn ⚙️ trước!")
        return ST_MENU

    if not cookies:
        await update.message.reply_text("❌ Chưa có cookie nào. Nhấn 🍪 để thêm!")
        return ST_MENU

    stop_ev = threading.Event()
    stop_flags[uid] = stop_ev

    task = asyncio.create_task(worker(uid, ctx.application))
    running_tasks[uid] = task

    await update.message.reply_text(
        f"✅ <b>Đã khởi động tool!</b>\n"
        f"🍪 {len(cookies)} cookie | ⏱ Delay {cfg.get('delay_min',5)}-{cfg.get('delay_max',15)}s\n"
        f"⚠️ Dừng sau {cfg.get('max_errors',5)} lỗi liên tiếp.\n"
        "Bot sẽ gửi thông báo cập nhật theo từng job.",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU

    if uid in stop_flags:
        stop_flags[uid].set()
    if uid in running_tasks:
        running_tasks[uid].cancel()
        running_tasks.pop(uid, None)
        stop_flags.pop(uid, None)
        await update.message.reply_text(
            "⏹ <b>Đã dừng tool!</b>\n"
            "Dùng 📊 để xem thống kê lần chạy vừa rồi.",
            parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
        )
    else:
        await update.message.reply_text("⚠️ Tool không đang chạy.", reply_markup=main_keyboard(True))
    return ST_MENU

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    stats = load_stats(uid)
    is_running = uid in running_tasks and not running_tasks[uid].done()

    if not stats:
        await update.message.reply_text("📭 Chưa có dữ liệu chạy nào.", reply_markup=main_keyboard(True))
        return ST_MENU

    status_icon = "🟢 Đang chạy" if is_running else "🔴 Đã dừng"
    await update.message.reply_text(
        f"📊 <b>THỐNG KÊ</b> [{status_icon}]\n"
        f"├ ⏰ Bắt đầu: {stats.get('started_at','N/A')}\n"
        f"├ 💰 Số dư ban đầu: {stats.get('balance','N/A')}\n"
        f"├ ✅ Job thành công: <b>{stats.get('job_done',0)}</b>\n"
        f"├ 💵 Tổng kiếm được: <b>{stats.get('earned',0)}₫</b>\n"
        f"├ 🍪 Cookie live: {stats.get('cookie_live',0)}/{stats.get('cookie_total',0)}\n"
        f"├ ❌ Cookie block: {stats.get('cookie_block',0)}\n"
        f"└ ⛔ Job block: {stats.get('job_block',0)}",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def cmd_viewcfg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    cfg     = load_config(uid)
    cookies = load_cookies(uid)

    if not cfg:
        await update.message.reply_text("❌ Chưa có cấu hình.", reply_markup=main_keyboard(True))
        return ST_MENU

    auth_preview = cfg["authorization"][:25] + "..." if cfg.get("authorization") else "Chưa có"
    proxy_bumx   = cfg.get("proxy_bumx") or "Không dùng"

    await update.message.reply_text(
        f"📋 <b>CẤU HÌNH HIỆN TẠI</b>\n\n"
        f"<b>🔐 BUMX Account</b>\n"
        f"├ Authorization: <code>{auth_preview}</code>\n"
        f"└ Proxy BUMX: <code>{proxy_bumx}</code>\n\n"
        f"<b>🍪 Cookie Facebook</b>\n"
        f"└ Tổng số: <b>{len(cookies)}</b> tài khoản (mỗi acc có proxy riêng)\n\n"
        f"<b>⚙️ Cài đặt chạy</b>\n"
        f"├ Đổi acc sau: <b>{cfg.get('tongjob',10)}</b> job\n"
        f"├ Delay job: <b>{cfg.get('delay_min',5)}-{cfg.get('delay_max',15)}</b>s\n"
        f"├ Delay API: <b>{cfg.get('api_min',2)}-{cfg.get('api_max',5)}</b>s\n"
        f"└ Lỗi liên tiếp tối đa: <b>{cfg.get('max_errors',5)}</b>",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /cancel - hủy thao tác hiện tại."""
    if is_key_valid():
        await update.message.reply_text("🔙 Đã huỷ.", reply_markup=main_keyboard(True))
        return ST_MENU
    else:
        await update.message.reply_text("🔙 Đã huỷ.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_key_valid():
        await update.message.reply_text("🔐 Bạn cần kích hoạt key trước.", reply_markup=main_keyboard(False))
        return ST_KEY_MENU
    await update.message.reply_text(
        "❓ <b>HƯỚNG DẪN SỬ DỤNG</b>\n\n"
        "<b>Bước 1 — Cấu hình Auth BUMX</b>\n"
        "Nhập authorization token lấy từ app BUMX\n\n"
        "<b>Bước 2 — Quản lý Cookie</b>\n"
        "Thêm cookie Facebook (có thể thêm nhiều acc, mỗi acc có proxy riêng)\n\n"
        "<b>Bước 3 — Cài đặt chạy</b>\n"
        "Cấu hình số job, delay, số lỗi liên tiếp tối đa\n\n"
        "<b>Bước 4 — Bắt đầu chạy</b>\n"
        "Bot sẽ tự động làm job và báo kết quả\n\n"
        "📌 <b>Loại nhiệm vụ hỗ trợ:</b>\n"
        "• 👍 Like Facebook — react bài viết\n"
        "• 💬 Like Poster — comment bài viết\n"
        "• ⭐ Review Facebook",
        parse_mode=ParseMode.HTML, reply_markup=main_keyboard(True),
    )
    return ST_MENU

async def handle_menu_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Cấu hình Auth" in text:
        return await menu_auth(update, ctx)
    elif "Quản lý Cookie" in text:
        return await menu_cookie(update, ctx)
    elif "Cài đặt chạy" in text:
        return await menu_settings(update, ctx)
    elif "Xem cấu hình" in text:
        return await cmd_viewcfg(update, ctx)
    elif "Bắt đầu chạy" in text:
        return await cmd_run(update, ctx)
    elif "Dừng tool" in text:
        return await cmd_stop(update, ctx)
    elif "Xem thống kê" in text:
        return await cmd_stats(update, ctx)
    elif "Trợ giúp" in text:
        return await cmd_help(update, ctx)
    elif "Liên hệ Admin" in text:
        await update.message.reply_text(
            "📞 <b>LIÊN HỆ ADMIN</b>\n\n"
            "• Lê Tuấn - @Bomaylatop1\n"
            "• Alex - @Dacvumeomeo19\n\n"
            "©️ <b>Bản quyền thuộc về Lê Tuấn và Alex</b>\n\n"
            "Mọi thắc mắc, góp ý hoặc cần hỗ trợ, vui lòng liên hệ trực tiếp qua Telegram.",
            parse_mode=ParseMode.HTML
        )
        return ST_MENU
    elif "Mua VPS" in text:
        await update.message.reply_text(
            "🚀 <b>MUA VPS GIÁ RẺ TẠI BVCLOUD</b>\n\n"
            "• CPU xeon mạnh mẽ\n"
            "• Ổ cứng SSD tốc độ cao\n"
            "• Băng thông không giới hạn\n"
            "• Hỗ trợ 24/7\n\n"
            "👉 Đặt mua ngay: http://bvzone.cloud/aff.php?aff=158\n\n"
            "Sử dụng mã giảm giá để được ưu đãi thêm!",
            parse_mode=ParseMode.HTML, disable_web_page_preview=False
        )
        return ST_MENU
    return ST_MENU

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            ST_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_text),
                CallbackQueryHandler(cb_cookie,   pattern="^ck_"),
                CallbackQueryHandler(cb_settings, pattern="^cfg_"),
            ],
            ST_KEY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_key_menu),
            ],
            ST_WAIT_FREE_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recv_free_key),
            ],
            ST_WAIT_VIP_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recv_vip_key),
            ],
            ST_WAIT_AUTH:         [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_auth)],
            ST_WAIT_AUTH_PROXY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_auth_proxy)],
            ST_WAIT_COOKIE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_cookie)],
            ST_WAIT_COOKIE_PROXY: [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_cookie_proxy)],
            ST_WAIT_TONGJOB: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recv_tongjob),
                CallbackQueryHandler(cb_settings, pattern="^cfg_"),
            ],
            ST_WAIT_DELAY_MIN:    [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_delay_min)],
            ST_WAIT_DELAY_MAX:    [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_delay_max)],
            ST_WAIT_API_MIN:      [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_api_min)],
            ST_WAIT_API_MAX:      [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_api_max)],
            ST_WAIT_MAX_ERRORS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, recv_max_errors)],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("run",   cmd_run))
    app.add_handler(CommandHandler("stop",  cmd_stop))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("help",  cmd_help))

    print("🤖 BUMX Bot đã khởi động với hệ thống KEY từ console (Device ID chỉ hiện khi nhập key)...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()