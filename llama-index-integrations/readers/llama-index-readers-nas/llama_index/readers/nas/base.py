import os
import fnmatch
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Union, List
from smb.SMBConnection import SMBConnection
from llama_index.core.readers.base import BasePydanticReader, BaseReader
from llama_index.core.schema import Document
from llama_index.core.bridge.pydantic import PrivateAttr, Field


class ProtocolStrategy(ABC):
    @abstractmethod
    def list_files(self, directory: str, pattern: str, recursive: bool) -> List[str]:
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        pass


class SMBStrategy(ProtocolStrategy):
    def __init__(self, nas_ip: str, username: str, password: str, share_name: str):
        self._conn = SMBConnection(username, password, "", "", use_ntlm_v2=True)
        self._conn.connect(nas_ip, 139)
        self.share_name = share_name

    def list_files(
        self, directory: str, pattern: str = "*", recursive: bool = True
    ) -> List[str]:
        files = []
        for item in self._conn.listPath(self.share_name, directory):
            if item.isDirectory:
                if recursive and item.filename not in [".", ".."]:
                    files.extend(
                        self.list_files(
                            os.path.join(directory, item.filename), pattern, recursive
                        )
                    )
            else:
                if fnmatch.fnmatch(item.filename, pattern):
                    files.append(os.path.join(directory, item.filename))
        return files

    def read_file(self, file_path: str) -> str:
        file_obj = self._conn.retrieveFile(self.share_name, file_path)
        return file_obj.read().decode("utf-8")


class NFSStrategy(ProtocolStrategy):
    def __init__(self, nas_path: str):
        self.nas_path = nas_path

    def list_files(
        self, directory: str, pattern: str = "*", recursive: bool = True
    ) -> List[str]:
        files = []
        for root, dirs, file_names in os.walk(directory):
            for filename in fnmatch.filter(file_names, pattern):
                files.append(os.path.join(root, filename))
            if not recursive:
                break
        return files

    def read_file(self, file_path: str) -> str:
        with open(file_path, encoding="utf-8") as file:
            return file.read()


class NASReader(BasePydanticReader):
    """
    NASReader reads files from a Network Attached Storage (NAS) system using a specified protocol.

    :param nas_ip: IP address of the NAS.
    :param nas_path: Path to the directory on the NAS.
    :param protocol: Protocol strategy used to connect to the NAS.
    :param username: Username for accessing the NAS (for smb).
    :param password: Password for accessing the NAS (for smb).
    :param share_name: Share name on the NAS (for smb).
    :param file_extractor: A mapping of file extension to a BaseReader class that specifies how to convert that file to text.
                           See `SimpleDirectoryReader` for more details.
    """

    SUPPORTED_PROTOCOLS = ["smb", "nfs"]

    nas_ip: str
    nas_path: str
    protocol: str
    username: Optional[str] = None
    password: Optional[str] = None
    share_name: Optional[str] = None
    file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = Field(
        default=None, exclude=True
    )

    _strategy = PrivateAttr(default=None)

    def __init__(
        self,
        nas_ip: str,
        nas_path: str,
        protocol: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        share_name: Optional[str] = None,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        **kwargs,
    ):
        self.nas_ip = nas_ip
        self.nas_path = nas_path
        self.protocol = protocol
        self.username = username
        self.password = password
        self.share_name = share_name

        if protocol == "smb":
            if not (username and password and share_name):
                raise ValueError(
                    "Username, password, and share_name are required for SMB protocol."
                )
            self._strategy = SMBStrategy(nas_ip, username, password, share_name)
        elif protocol == "nfs":
            self._strategy = NFSStrategy(nas_path)
        else:
            raise ValueError(
                f"Unsupported protocol '{protocol}'. Supported protocols are: {self.SUPPORTED_PROTOCOLS}."
            )

        super().__init__(
            nas_ip=nas_ip,
            nas_path=nas_path,
            protocol=protocol,
            username=username,
            password=password,
            share_name=share_name,
            file_extractor=file_extractor,
            **kwargs,
        )

    def list_files(self, pattern="*", recursive=True) -> List[str]:
        """List all files in the NAS path that match the pattern."""
        return self._strategy.list_files(self.nas_path, pattern, recursive)

    def read_file(self, file_path: str) -> str:
        """Read the content of a file."""
        return self._strategy.read_file(file_path)

    def load_data(self, pattern="*", recursive=True) -> List[Document]:
        """Load data from NAS and return as a list of SimpleDocument."""
        documents = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_path in self.list_files(pattern, recursive):
                content = self.read_file(file_path)
                local_file_path = os.path.join(temp_dir, os.path.basename(file_path))
                with open(local_file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                documents.append(
                    Document(text=content, metadata={"file_path": file_path})
                )
        return documents
