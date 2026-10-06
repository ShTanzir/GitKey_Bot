import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from keystore import KeystoreConfig, KeystoreResult


@dataclass
class UserSession:
    user_id: int
    current_state: str = "MAIN_MENU" # MAIN_MENU, WIZARD, TOOL_WAITING_INPUT, SETTINGS
    wizard_step: str = "" # PROJECT_NAME, LOGO, ALIAS, STORE_PASS, KEY_PASS, ADVANCED_ALGORITHM, ADVANCED_KEYSIZE, ADVANCED_VALIDITY, ADVANCED_CN, ADVANCED_ORG, CONFIRM
    draft_config: KeystoreConfig = field(default_factory=KeystoreConfig)
    last_result: Optional[KeystoreResult] = None
    active_tool: Optional[str] = None
    hide_secrets: bool = True
    confirm_before_export: bool = True
    temp_dir: Optional[str] = None


@dataclass
class HistoryMetadata:
    id: str
    project_name: str
    alias: str
    filename: str
    timestamp: float
    sha256_fingerprint: str
    algorithm: str


class SessionManager:
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
        self._history: Dict[int, List[HistoryMetadata]] = {}

    def get_session(self, user_id: int) -> UserSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        return self._sessions[user_id]

    def reset_session(self, user_id: int):
        session = self.get_session(user_id)
        session.current_state = "MAIN_MENU"
        session.wizard_step = ""
        session.draft_config = KeystoreConfig()
        session.active_tool = None

    def add_history(self, user_id: int, result: KeystoreResult):
        if user_id not in self._history:
            self._history[user_id] = []
        
        meta = HistoryMetadata(
            id=f"{user_id}_{int(time.time())}",
            project_name=result.project_name,
            alias=result.alias,
            filename=result.filename,
            timestamp=time.time(),
            sha256_fingerprint=result.sha256_fingerprint,
            algorithm=result.certificate_info.split('\n')[-1] if result.certificate_info else "RSA"
        )
        self._history[user_id].insert(0, meta)
        # Keep max 10 items
        if len(self._history[user_id]) > 10:
            self._history[user_id] = self._history[user_id][:10]

    def get_history(self, user_id: int) -> List[HistoryMetadata]:
        return self._history.get(user_id, [])

    def delete_history_item(self, user_id: int, item_id: str):
        if user_id in self._history:
            self._history[user_id] = [m for m in self._history[user_id] if m.id != item_id]


session_manager = SessionManager()
