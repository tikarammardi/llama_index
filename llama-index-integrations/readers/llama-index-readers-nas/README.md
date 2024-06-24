# NAS Reader

```bash
pip install llama-index-readers-nas-reader

```

This loader reads files from a Network Attached Storage (NAS) system using the following protocols:

- SMB (Server Message Block)
- NFS (Network File System)

It supports recursively traversing and downloading files from subfolders and provides the capability to download only files with specific patterns. To use this loader, you need to specify the protocol, along with necessary credentials and paths.

### Subfolder Traversing (enabled by default)

To disable: `loader.load_data(recursive=False)`

## Usage

## SMB Protocol

To read files from a NAS using the SMB protocol, provide the NAS IP address, username, password, share name, and the path to the directory on the NAS:

### Example Usage:

```bash
from llama_index.readers.nas_reader import NASReader

reader = NASReader(
    nas_ip="192.168.1.100",
    protocol="smb",
    username="user",
    password="pass",
    share_name="share",
    nas_path="/path/to/directory"
)
documents = reader.load_data(pattern="*.txt", recursive=True)
for doc in documents:
    print(doc.text)

```

## NFS Protocol

To read files from a NAS using the NFS protocol, provide the NAS IP address, protocol, and the path to the directory on the NAS:

### Example Usage:

```bash
from llama_index.readers.nas_reader import NASReader

reader = NASReader(
    nas_ip="192.168.1.100",
    protocol="nfs",
    nas_path="/path/to/nfs/mount"
)
documents = reader.load_data(pattern="*.txt", recursive=True)
for doc in documents:
    print(doc.text)

```

### Contributing

Contributions to the NAS Reader are welcome! If you have any improvements or new features to add, please create a pull request.

### License

This project is licensed under the MIT License.

Author
https://github.com/tikarammardi

This loader is designed to be used as a way to load data into LlamaIndex.
