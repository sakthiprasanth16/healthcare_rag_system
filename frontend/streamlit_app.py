import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FIXED_USER_ID = "user_" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "prasanth_mediassist"))[:8]

st.set_page_config(
    page_title="Patient Medical Record Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f0f 0%, #141414 100%) !important;
    border-right: 1px solid #262626 !important;
    min-width: 280px !important;
    max-width: 280px !important;
    transform: none !important;
    display: block !important;
    visibility: visible !important;
    left: 0 !important;
    position: relative !important;
}
[data-testid="stSidebar"] * { color: #e5e5e5; }
[data-testid="collapsedControl"] { display: none !important; }
button[kind="header"] { display: none !important; }
section[data-testid="stSidebar"] > div:first-child > div > button { display: none !important; }
.chat-scroll { max-height: 300px; overflow-y: auto; padding-right: 4px; }
.chat-scroll::-webkit-scrollbar { width: 4px; }
.chat-scroll::-webkit-scrollbar-track { background: #1a1a1a; }
.chat-scroll::-webkit-scrollbar-thumb { background: #404040; border-radius: 4px; }
.stApp { background-color: #1a1a1a; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem !important; max-width: 900px !important; }
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    border: none !important; border-radius: 10px !important;
    color: white !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.35) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important; border: none !important;
    border-radius: 8px !important; color: #d4d4d4 !important;
    font-size: 13px !important; font-weight: 400 !important;
    text-align: left !important; padding: 6px 10px !important;
    transition: background 0.15s !important;
    white-space: nowrap !important; overflow: hidden !important;
    text-overflow: ellipsis !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #262626 !important; color: #ffffff !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: #1e1e1e !important; color: #e5e5e5 !important;
    border: 1px solid #333 !important; border-radius: 8px !important;
    font-size: 12px !important; padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 2px rgba(16,185,129,0.15) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: #525252 !important; }
[data-testid="stSidebar"] .stTextInput > label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #1e1e1e !important; border: 2px dashed #404040 !important;
    border-radius: 10px !important; cursor: pointer !important;
    transition: border-color 0.2s, background 0.2s !important;
    min-height: 160px !important; display: flex !important;
    align-items: center !important; justify-content: center !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #10b981 !important; background: #1a2a1e !important;
}
[data-testid="stFileUploaderDropzone"] > div { display: none !important; }
[data-testid="stFileUploader"] > label + div > div:last-child,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] > div:last-child { display: none !important; }
[data-testid="stFileUploaderDropzone"] button { display: none !important; }
.user-msg { display: flex; justify-content: flex-end; margin: 12px 0; }
.user-bubble {
    background: linear-gradient(135deg, #10b981, #059669); color: white;
    border-radius: 18px 18px 4px 18px; padding: 12px 18px;
    max-width: 75%; font-size: 14.5px; line-height: 1.6;
    box-shadow: 0 2px 8px rgba(16,185,129,0.25);
}
.assistant-msg { display: flex; justify-content: flex-start; margin: 12px 0; }
.assistant-bubble {
    background: #252525; color: #e5e5e5;
    border-radius: 18px 18px 18px 4px; padding: 14px 18px;
    max-width: 80%; font-size: 14.5px; line-height: 1.7;
    border: 1px solid #333; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin: 4px 8px 0 8px; flex-shrink: 0;
}
.user-avatar { background: #059669; }
.bot-avatar { background: #1e3a5f; }
.pdf-panel {
    background: #1e1e1e; border: 1px solid #333;
    border-radius: 12px; padding: 16px; margin-bottom: 12px;
}
.pdf-item {
    display: flex; align-items: center; justify-content: space-between;
    background: #252525; border-radius: 8px;
    padding: 10px 14px; margin: 6px 0;
    font-size: 13px; color: #d4d4d4; border: 1px solid #333;
}
.pdf-badge { background: #10b981; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 600; }
.sidebar-section {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #737373 !important; padding: 8px 4px 4px 4px;
}
.date-header {
    font-size: 10px; font-weight: 600; color: #525252 !important;
    padding: 8px 4px 2px 4px; letter-spacing: 0.05em;
    border-top: 1px solid #262626; margin-top: 4px;
}
.howto-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 12px; margin-top: 8px; }
.howto-step { display: flex; align-items: flex-start; gap: 8px; margin: 6px 0; font-size: 12px; color: #a3a3a3; }
.step-num {
    background: #10b981; color: white; border-radius: 50%;
    width: 18px; height: 18px; display: flex; align-items: center;
    justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.instruction-banner {
    background: #1c2a1e; border: 1px solid #2d4a30;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 20px;
    display: flex; align-items: flex-start; gap: 12px;
}
.instruction-banner span { color: #86efac; font-size: 13.5px; line-height: 1.6; }
.stTextInput input {
    background: #252525 !important; color: #e5e5e5 !important;
    border: 1px solid #404040 !important; border-radius: 12px !important;
    font-size: 14px !important; padding: 12px 16px !important;
}
.stTextInput input:focus { border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; }
[data-testid="stExpander"] { background: #252525 !important; border: 1px solid #333 !important; border-radius: 12px !important; }
.stTextInput > label { color: #a3a3a3 !important; font-size: 12px !important; }
#MainMenu, footer { display: none !important; }
/* Delete confirm box */
.delete-confirm-box {
    background: #1e1010; border: 1px solid #7f1d1d;
    border-radius: 10px; padding: 14px 16px; margin: 6px 0;
}
.disclaimer-box {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 10px 12px; margin-top: 8px;
    font-size: 11px; color: #737373 !important; line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "user_id": FIXED_USER_ID,
        "current_session_id": None,
        "messages": [],
        "sessions_list": [],
        "session_titled": False,
        "renaming_session": None,
        "rename_value": "",
        "pdf_indexed": False,
        "upload_success": None,
        "indexed_pdfs": [],
        "recycled_pdfs": [],
        "show_pdf_panel": False,
        "search_query": "",
        # NEW: delete confirmation state
        "confirming_delete_session": None,
        "delete_confirm_input": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════
def api_get_sessions():
    try:
        r = requests.get(f"{BACKEND_URL}/sessions/{FIXED_USER_ID}", timeout=5)
        return r.json().get("sessions", []) if r.status_code == 200 else []
    except: return []

def refresh_session_lists():
    st.session_state.sessions_list = sorted(
        api_get_sessions(),
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )

def api_get_messages(session_id):
    try:
        r = requests.get(f"{BACKEND_URL}/history/{FIXED_USER_ID}/{session_id}", timeout=5)
        return r.json().get("messages", []) if r.status_code == 200 else []
    except: return []

def api_get_session_files(session_id):
    try:
        r = requests.get(f"{BACKEND_URL}/session-files/{session_id}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            indexed = [f["file_name"] for f in data.get("indexed_files", [])]
            recycled = data.get("recycled_files", [])
            return indexed, recycled
    except: pass
    return [], []

def api_create_session(session_id, title="New Record"):
    try:
        requests.post(f"{BACKEND_URL}/sessions/{FIXED_USER_ID}/{session_id}",
                      params={"title": title}, timeout=5)
    except: pass

def api_rename_session(session_id, title):
    try:
        requests.put(f"{BACKEND_URL}/sessions/{session_id}/rename",
                     json={"title": title}, timeout=5)
    except: pass

def api_pin_session(session_id):
    try:
        r = requests.put(f"{BACKEND_URL}/sessions/{session_id}/pin", timeout=5)
        return r.json().get("pinned", False) if r.status_code == 200 else False
    except: return False

def api_permanent_delete_session(session_id):
    """Directly permanently delete a session (no recycle bin)."""
    try:
        r = requests.delete(
            f"{BACKEND_URL}/sessions/{FIXED_USER_ID}/{session_id}/permanent",
            timeout=5
        )
        return r.status_code == 200
    except: return False

def api_recycle_doc(file_name):
    try:
        r = requests.post(f"{BACKEND_URL}/document/recycle", json={
            "user_id": FIXED_USER_ID,
            "session_id": st.session_state.current_session_id,
            "file_name": file_name
        }, timeout=5)
        return r.status_code == 200
    except: return False

def api_restore_doc(file_name):
    try:
        r = requests.post(f"{BACKEND_URL}/document/restore", json={
            "user_id": FIXED_USER_ID,
            "session_id": st.session_state.current_session_id,
            "file_name": file_name
        }, timeout=5)
        return r.status_code == 200
    except: return False

def api_permanent_delete_doc(file_name):
    try:
        r = requests.delete(f"{BACKEND_URL}/document/permanent", json={
            "user_id": FIXED_USER_ID,
            "session_id": st.session_state.current_session_id,
            "file_name": file_name
        }, timeout=5)
        return r.status_code == 200
    except: return False


# ══════════════════════════════════════════════════════════
# UPLOAD HELPER
# ══════════════════════════════════════════════════════════
def do_upload(file_obj, progress_bar, status_box):
    import time
    files = {"file": (file_obj.name, file_obj.getvalue(), "application/pdf")}
    data = {"user_id": FIXED_USER_ID, "session_id": st.session_state.current_session_id}
    status_box.info("📄 **Step 1/4** — Reading PDF file...")
    progress_bar.progress(10); time.sleep(0.8)
    status_box.info("🔍 **Step 2/4** — Validating medical content with Gemini...")
    progress_bar.progress(30); time.sleep(0.8)
    status_box.info("🧠 **Step 3/4** — Chunking & embedding with PubMedBERT...")
    progress_bar.progress(60)
    r = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=300)
    status_box.info("💾 **Step 4/4** — Storing vectors in Pinecone...")
    progress_bar.progress(85); time.sleep(0.5)
    if r.status_code == 200:
        progress_bar.progress(100)
        status_box.empty(); progress_bar.empty()
        return r.json()
    else:
        progress_bar.empty(); status_box.empty()
        st.error(f"❌ {r.json().get('detail', r.text)}")
        return None


# ══════════════════════════════════════════════════════════
# ACTIONS
# ══════════════════════════════════════════════════════════
def start_new_chat():
    sid = str(uuid.uuid4())[:8]
    st.session_state.current_session_id = sid
    st.session_state.messages = []
    st.session_state.session_titled = False
    st.session_state.renaming_session = None
    st.session_state.pdf_indexed = False
    st.session_state.upload_success = None
    st.session_state.indexed_pdfs = []
    st.session_state.recycled_pdfs = []
    st.session_state.show_pdf_panel = False
    st.session_state.search_query = ""
    st.session_state.confirming_delete_session = None
    st.session_state.delete_confirm_input = ""
    api_create_session(sid, "New Record")
    st.session_state.sessions_list = api_get_sessions()

def load_session(session_id):
    st.session_state.current_session_id = session_id
    st.session_state.messages = api_get_messages(session_id)
    st.session_state.session_titled = True
    st.session_state.renaming_session = None
    st.session_state.upload_success = None
    st.session_state.show_pdf_panel = False
    st.session_state.confirming_delete_session = None
    st.session_state.delete_confirm_input = ""
    indexed, recycled = api_get_session_files(session_id)
    st.session_state.indexed_pdfs = indexed
    st.session_state.recycled_pdfs = recycled
    st.session_state.pdf_indexed = len(indexed) > 0 or len(st.session_state.messages) > 0


# ══════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════
if st.session_state.current_session_id is None:
    refresh_session_lists()
    if st.session_state.sessions_list:
        latest = st.session_state.sessions_list[0]
        load_session(latest["session_id"])
    else:
        start_new_chat()


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🩺 Patient Medical Record Assistant")
    st.markdown("---")

    if st.button("✏️  New Record", use_container_width=True, type="primary"):
        start_new_chat(); st.rerun()

    st.markdown("---")

    # ── Embedded Documents Panel ──
    if st.session_state.indexed_pdfs:
        st.markdown('<div class="sidebar-section">📄 Embedded Documents</div>', unsafe_allow_html=True)
        for file_name in list(st.session_state.indexed_pdfs):
            if file_name not in st.session_state.recycled_pdfs:
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"<div style='font-size:12px;color:#d4d4d4;padding:4px 0;'>📑 {file_name[:26]}</div>", unsafe_allow_html=True)
                if c2.button("🗑", key=f"recycle_doc_{file_name}", help="Move to Recycle Bin"):
                    if api_recycle_doc(file_name):
                        st.session_state.recycled_pdfs.append(file_name)
                        st.rerun()

    # ── Document Recycle Bin ──
    if st.session_state.recycled_pdfs:
        st.markdown('<div class="sidebar-section">🗑️ Document Recycle Bin</div>', unsafe_allow_html=True)
        for file_name in list(st.session_state.recycled_pdfs):
            st.markdown(f"<div style='font-size:11px;color:#737373;padding:2px 4px;'>🗂 {file_name[:26]}</div>", unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            if rc1.button("🔄 Restore", key=f"restore_doc_{file_name}"):
                if api_restore_doc(file_name):
                    st.session_state.recycled_pdfs.remove(file_name)
                    st.rerun()
            if rc2.button("❌ Delete", key=f"perm_doc_{file_name}"):
                if api_permanent_delete_doc(file_name):
                    st.session_state.recycled_pdfs.remove(file_name)
                    if file_name in st.session_state.indexed_pdfs:
                        st.session_state.indexed_pdfs.remove(file_name)
                    st.rerun()

    st.markdown("---")

    sessions = st.session_state.sessions_list
    pinned = [s for s in sessions if s.get("pinned")]
    recent = [s for s in sessions if not s.get("pinned")]

    # ── Pinned Sessions ──
    if pinned:
        st.markdown('<div class="sidebar-section">📌 Pinned</div>', unsafe_allow_html=True)
        for s in pinned:
            sid = s.get("session_id")
            title = s.get("title", "Record")
            display = (title[:26] + "…") if len(title) > 26 else title
            is_active = sid == st.session_state.current_session_id

            # ── Delete confirmation mode ──
            if st.session_state.confirming_delete_session == sid:
                st.markdown(f'<div class="delete-confirm-box">', unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:12px;color:#fca5a5;margin-bottom:6px;'>Type <b style='color:#f87171;'>{title[:30]}</b> to confirm delete:</div>", unsafe_allow_html=True)
                typed = st.text_input("confirm_del", key=f"del_input_{sid}", placeholder="Type record name...", label_visibility="collapsed")
                dc1, dc2 = st.columns(2)
                with dc1:
                    confirmed = typed.strip() == title.strip()
                    if st.button("🗑 Delete", key=f"confirm_del_btn_{sid}", type="primary", use_container_width=True, disabled=not confirmed):
                        if api_permanent_delete_session(sid):
                            if sid == st.session_state.current_session_id:
                                start_new_chat()
                            else:
                                st.session_state.sessions_list = api_get_sessions()
                            st.session_state.confirming_delete_session = None
                            st.rerun()
                with dc2:
                    if st.button("Cancel", key=f"cancel_del_{sid}", use_container_width=True):
                        st.session_state.confirming_delete_session = None; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                continue

            c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
            with c1:
                btn_label = f"📌 ▶ {display}" if is_active else f"📌 {display}"
                if st.button(btn_label, key=f"load_{sid}", use_container_width=True, type="secondary"):
                    load_session(sid); st.rerun()
            with c2:
                if st.button("✏️", key=f"ren_{sid}", help="Rename"):
                    st.session_state.renaming_session = sid
                    st.session_state.rename_value = title; st.rerun()
            with c3:
                if st.button("📌", key=f"pin_{sid}", help="Unpin"):
                    api_pin_session(sid)
                    st.session_state.sessions_list = api_get_sessions(); st.rerun()
            with c4:
                if st.button("🗑", key=f"del_{sid}", help="Delete"):
                    st.session_state.confirming_delete_session = sid; st.rerun()
        st.markdown("---")

    # ── Search + Recent Records ──
    st.markdown('<div class="sidebar-section">🗂️ Recent Records</div>', unsafe_allow_html=True)
    search_query = st.text_input(
        "search", value=st.session_state.search_query,
        placeholder="🔍  Search records...",
        label_visibility="collapsed", key="sidebar_search"
    )
    st.session_state.search_query = search_query

    if search_query.strip():
        filtered_recent = [s for s in recent if search_query.strip().lower() in s.get("title", "").lower()]
        if not filtered_recent:
            st.markdown(f'<div style="color:#525252;font-size:12px;padding:6px 4px;">No records matching "<b style=color:#a3a3a3>{search_query}</b>"</div>', unsafe_allow_html=True)
    else:
        filtered_recent = recent

    if not filtered_recent and not search_query.strip():
        st.markdown('<div style="color:#525252;font-size:13px;padding:8px 4px;">No records yet.</div>', unsafe_allow_html=True)
    else:
        from collections import defaultdict
        date_groups = defaultdict(list)
        for s in filtered_recent:
            raw_date = s.get("updated_at", s.get("created_at", ""))
            try: date_label = raw_date[:10]
            except: date_label = "Unknown"
            date_groups[date_label].append(s)

        sorted_dates = sorted(date_groups.keys(), reverse=True)

        st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
        for date_label in sorted_dates:
            st.markdown(f'<div class="date-header">📅 {date_label}</div>', unsafe_allow_html=True)
            for s in date_groups[date_label]:
                sid = s.get("session_id")
                title = s.get("title", "New Record")
                display = (title[:26] + "…") if len(title) > 26 else title
                is_active = sid == st.session_state.current_session_id

                # ── Rename mode ──
                if st.session_state.renaming_session == sid:
                    new_title = st.text_input("", value=st.session_state.rename_value,
                                              key=f"rename_input_{sid}", placeholder="Enter new name...")
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if st.button("✅ Save", key=f"save_ren_{sid}", use_container_width=True, type="primary"):
                            if new_title.strip():
                                api_rename_session(sid, new_title.strip())
                                st.session_state.sessions_list = api_get_sessions()
                            st.session_state.renaming_session = None; st.rerun()
                    with rc2:
                        if st.button("❌ Cancel", key=f"cancel_ren_{sid}", use_container_width=True):
                            st.session_state.renaming_session = None; st.rerun()
                    continue

                # ── Delete confirmation mode ──
                if st.session_state.confirming_delete_session == sid:
                    st.markdown(f'<div class="delete-confirm-box">', unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:12px;color:#fca5a5;margin-bottom:6px;'>Type <b style='color:#f87171;'>{title[:30]}</b> to confirm delete:</div>", unsafe_allow_html=True)
                    typed = st.text_input("confirm", key=f"del_input_{sid}", placeholder="Type record name...", label_visibility="collapsed")
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        confirmed = typed.strip() == title.strip()
                        if st.button("🗑 Delete", key=f"confirm_del_btn_{sid}", type="primary", use_container_width=True, disabled=not confirmed):
                            if api_permanent_delete_session(sid):
                                if sid == st.session_state.current_session_id:
                                    start_new_chat()
                                else:
                                    st.session_state.sessions_list = api_get_sessions()
                                st.session_state.confirming_delete_session = None
                                st.rerun()
                    with dc2:
                        if st.button("Cancel", key=f"cancel_del_{sid}", use_container_width=True):
                            st.session_state.confirming_delete_session = None; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    continue

                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                with c1:
                    btn_label = f"▶ {display}" if is_active else display
                    if st.button(btn_label, key=f"load_{sid}", use_container_width=True, type="secondary"):
                        load_session(sid); st.rerun()
                with c2:
                    if st.button("✏️", key=f"ren_{sid}", help="Rename"):
                        st.session_state.renaming_session = sid
                        st.session_state.rename_value = title; st.rerun()
                with c3:
                    if st.button("📌", key=f"pin_{sid}", help="Pin"):
                        api_pin_session(sid)
                        st.session_state.sessions_list = api_get_sessions(); st.rerun()
                with c4:
                    if st.button("🗑", key=f"del_{sid}", help="Delete"):
                        st.session_state.confirming_delete_session = sid; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── How to Use ──
    st.markdown('<div class="sidebar-section">💡 How to Use</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="howto-card">
        <div class="howto-step"><div class="step-num">1</div><span>Click <b>New Record</b> for each new session</span></div>
        <div class="howto-step"><div class="step-num">2</div><span>Upload a medical PDF — lab report, prescription, or doctor notes</span></div>
        <div class="howto-step"><div class="step-num">3</div><span>Click <b>🧬 Embed PDF</b> and wait for all 4 steps</span></div>
        <div class="howto-step"><div class="step-num">4</div><span>Ask questions — use 📎 to add more PDFs</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Disclaimer in sidebar ──
    st.markdown("""
    <div class="disclaimer-box">
        ⚠️ This assistant is for <b>informational purposes only</b> and does not provide medical advice.
        Always consult a qualified physician for medical decisions.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════
current_title = "New Record"
for s in st.session_state.sessions_list:
    if s.get("session_id") == st.session_state.current_session_id:
        current_title = s.get("title", "New Record")
        break

st.markdown(f"<h2 style='color:#e5e5e5;font-weight:600;margin-bottom:4px;'>🩺 {current_title}</h2>", unsafe_allow_html=True)
# REMOVED: "Powered by PubMedBERT + Gemini" subtitle

# ── How to Use in main area — only when no PDF uploaded yet ──
if not st.session_state.pdf_indexed and not st.session_state.messages:
    st.markdown("""
    <div class="instruction-banner">
        <span style="font-size:20px">👋</span>
        <span><b style="color:#ffffff;">How to get started:</b><br>
        Upload a medical PDF (lab report, prescription, doctor notes) → Click <b>🧬 Embed PDF</b> → Then ask questions.</span>
    </div>
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;margin-bottom:16px;">
        <div style="font-size:12px;font-weight:600;color:#737373;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">💡 How to Use</div>
        <div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;font-size:13px;color:#a3a3a3;">
            <div style="background:#10b981;color:white;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">1</div>
            <span>Click <b style="color:#d4d4d4;">New Record</b> for each new session</span>
        </div>
        <div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;font-size:13px;color:#a3a3a3;">
            <div style="background:#10b981;color:white;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">2</div>
            <span>Upload a medical PDF — lab report, prescription, or doctor notes</span>
        </div>
        <div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;font-size:13px;color:#a3a3a3;">
            <div style="background:#10b981;color:white;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">3</div>
            <span>Click <b style="color:#d4d4d4;">🧬 Embed PDF</b> and wait for all 4 steps</span>
        </div>
        <div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;font-size:13px;color:#a3a3a3;">
            <div style="background:#10b981;color:white;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">4</div>
            <span>Ask questions — use 📎 to add more PDFs</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Upload Expander ──
with st.expander("📎 Upload Medical PDF", expanded=not st.session_state.pdf_indexed):
    st.markdown("""
    <div style="pointer-events:none;text-align:center;position:relative;z-index:1;margin-bottom:-175px;padding-top:28px;">
        <div style="font-size:40px;line-height:1;">📂</div>
        <div style="color:#a3a3a3;font-size:14px;margin-top:10px;">Drop your lab report, prescription, or medical document here</div>
        <div style="color:#525252;font-size:12px;margin-top:6px;">📄 PDF only &nbsp;·&nbsp; 200MB per file</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload", type=["pdf"], accept_multiple_files=False,
        key=f"uploader_{st.session_state.current_session_id}",
        label_visibility="collapsed"
    )

    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) // 1024
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;background:#252525;
        border:1px solid #333;border-radius:8px;padding:10px 14px;margin:10px 0;">
            <span style="font-size:20px;">📄</span>
            <div>
                <div style="color:#e5e5e5;font-size:13px;font-weight:500;">{uploaded_file.name}</div>
                <div style="color:#737373;font-size:11px;">{size_kb} KB · PDF</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        already_indexed = uploaded_file.name in st.session_state.indexed_pdfs
        if already_indexed:
            st.info(f"✅ **{uploaded_file.name}** is already embedded.")
        else:
            if st.button("🧬 Embed PDF", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_box = st.empty()
                try:
                    result = do_upload(uploaded_file, progress_bar, status_box)
                    if result:
                        st.session_state.upload_success = (
                            f"✅ **{uploaded_file.name}** is a valid medical document — embedded successfully!\n\n"
                            f"📊 **{result.get('chunks_embedded', result.get('chunks_stored', '?'))}** chunks · "
                            f"📄 **{result.get('pages', result.get('pages_processed', '?'))}** pages · "
                            f"🔍 Validated via **{result.get('validated_via', result.get('validation_method', 'gemini'))}**"
                        )
                        st.session_state.pdf_indexed = True
                        if uploaded_file.name not in st.session_state.indexed_pdfs:
                            st.session_state.indexed_pdfs.append(uploaded_file.name)
                        if not st.session_state.session_titled:
                            title = f"📄 {uploaded_file.name[:45]}"
                            api_rename_session(st.session_state.current_session_id, title)
                            st.session_state.session_titled = True
                            st.session_state.sessions_list = api_get_sessions()
                        st.rerun()
                except Exception as e:
                    progress_bar.empty(); status_box.empty()
                    st.error(f"❌ Connection error: {str(e)}")

if st.session_state.upload_success:
    st.success(st.session_state.upload_success)
    if st.session_state.messages:
        st.session_state.upload_success = None

# ── PDF Panel ──
if st.session_state.show_pdf_panel:
    st.markdown('<div class="pdf-panel">', unsafe_allow_html=True)
    st.markdown("**📂 Documents in this session:**")
    if st.session_state.indexed_pdfs:
        for pdf_name in st.session_state.indexed_pdfs:
            badge = '<span style="background:#b91c1c;color:white;border-radius:4px;padding:2px 8px;font-size:10px;font-weight:600;">🗑 Recycled</span>' if pdf_name in st.session_state.recycled_pdfs else '<span style="background:#10b981;color:white;border-radius:4px;padding:2px 8px;font-size:10px;font-weight:600;">✅ Embedded</span>'
            st.markdown(f'<div class="pdf-item"><span>📄 {pdf_name}</span>{badge}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#737373;font-size:13px;">No documents embedded yet.</div>', unsafe_allow_html=True)

    st.markdown("**➕ Add another medical PDF:**")
    st.markdown("""
    <div style="pointer-events:none;text-align:center;position:relative;z-index:1;margin-bottom:-175px;padding-top:28px;">
        <div style="font-size:36px;line-height:1;">📂</div>
        <div style="color:#a3a3a3;font-size:13px;margin-top:8px;">Drop additional medical document here</div>
        <div style="color:#525252;font-size:11px;margin-top:4px;">📄 PDF only &nbsp;·&nbsp; 200MB per file</div>
    </div>
    """, unsafe_allow_html=True)

    extra_file = st.file_uploader(
        "Upload additional document", type=["pdf"], accept_multiple_files=False,
        key=f"extra_uploader_{st.session_state.current_session_id}_{len(st.session_state.indexed_pdfs)}",
        label_visibility="collapsed"
    )
    if extra_file:
        if extra_file.name in st.session_state.indexed_pdfs:
            st.warning(f"⚠️ **{extra_file.name}** is already embedded.")
        else:
            size_kb = len(extra_file.getvalue()) // 1024
            st.markdown(f"📄 **{extra_file.name}** · {size_kb} KB")
            if st.button("🧬 Embed This PDF", type="primary", key="extra_embed_btn"):
                progress_bar2 = st.progress(0)
                status_box2 = st.empty()
                try:
                    result2 = do_upload(extra_file, progress_bar2, status_box2)
                    if result2:
                        st.session_state.indexed_pdfs.append(extra_file.name)
                        st.session_state.upload_success = (
                            f"✅ **{extra_file.name}** added & embedded!\n\n"
                            f"📊 **{result2.get('chunks_embedded', result2.get('chunks_stored', '?'))}** chunks · "
                            f"📄 **{result2.get('pages', result2.get('pages_processed', '?'))}** pages\n\n"
                            f"💬 Now asking from **{len(st.session_state.indexed_pdfs)} documents**."
                        )
                        st.session_state.show_pdf_panel = False
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")

    if st.button("✖ Close", key="close_pdf_panel"):
        st.session_state.show_pdf_panel = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Chat Messages ──
chat_area = st.container()
with chat_area:
    if not st.session_state.messages and st.session_state.pdf_indexed:
        st.markdown("""
        <div style="text-align:center;padding:30px 20px;color:#737373;">
            <div style="font-size:32px;margin-bottom:8px;">💬</div>
            <div style="color:#a3a3a3;font-size:14px;margin-bottom:16px;">Record embedded! Ask your first question below.</div>
            <div>
                <span style="display:inline-block;background:#252525;border:1px solid #333;border-radius:20px;padding:8px 16px;margin:4px;font-size:13px;color:#a3a3a3;">🔬 What are the abnormal values?</span>
                <span style="display:inline-block;background:#252525;border:1px solid #333;border-radius:20px;padding:8px 16px;margin:4px;font-size:13px;color:#a3a3a3;">💊 What medications are recommended?</span>
            </div>
            <div style="margin-top:6px;">
                <span style="display:inline-block;background:#252525;border:1px solid #333;border-radius:20px;padding:8px 16px;margin:4px;font-size:13px;color:#a3a3a3;">📋 Summarize the doctor's notes</span>
                <span style="display:inline-block;background:#252525;border:1px solid #333;border-radius:20px;padding:8px 16px;margin:4px;font-size:13px;color:#a3a3a3;">📊 What is my cholesterol level?</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.messages:
        for msg in st.session_state.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                st.markdown(f"""
                <div class="user-msg">
                    <div class="user-bubble">{content}</div>
                    <div class="avatar user-avatar">👤</div>
                </div>""", unsafe_allow_html=True)
            else:
                # REMOVED: sources tags — answer only
                st.markdown(f"""
                <div class="assistant-msg">
                    <div class="avatar bot-avatar">🤖</div>
                    <div class="assistant-bubble">{content}</div>
                </div>""", unsafe_allow_html=True)

# ── Chat Input ──
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

if st.session_state.pdf_indexed or st.session_state.messages:
    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_attach, col_send = st.columns([8, 1, 1])
        with col_input:
            user_input = st.text_input("msg", placeholder="Ask anything about your medical record...", label_visibility="collapsed")
        with col_attach:
            attach_clicked = st.form_submit_button("📎", use_container_width=True, help="Add more PDFs")
        with col_send:
            submitted = st.form_submit_button("➤", use_container_width=True, type="primary")

    if attach_clicked:
        st.session_state.show_pdf_panel = not st.session_state.show_pdf_panel; st.rerun()

    if submitted and user_input.strip():
        question = user_input.strip()
        if not st.session_state.session_titled:
            title = (question[:52] + "…") if len(question) > 52 else question
            api_rename_session(st.session_state.current_session_id, title)
            st.session_state.session_titled = True
            st.session_state.sessions_list = api_get_sessions()

        st.session_state.messages.append({"role": "user", "content": question, "sources": []})

        with st.spinner("🔍 Searching medical records..."):
            try:
                r = requests.post(f"{BACKEND_URL}/chat", json={
                    "user_id": FIXED_USER_ID,
                    "session_id": st.session_state.current_session_id,
                    "question": question
                }, timeout=60)
                if r.status_code == 200:
                    result = r.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", [])
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ {r.json().get('detail', r.text)}",
                        "sources": []
                    })
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {str(e)}", "sources": []})
        st.rerun()
else:
    st.markdown("""
    <div style="background:#1a1a1a;border:1px dashed #333;border-radius:12px;
    padding:14px 18px;color:#525252;font-size:13px;text-align:center;">
        🔒 Upload and embed a medical PDF above to enable chat
    </div>
    """, unsafe_allow_html=True)