# psycoudbtv

`psycoudbtv` 是 [pgvector-python](https://github.com/pgvector/pgvector-python) 的改名分支，用于在 **UNVDB / UDB-TV** 等 PostgreSQL 兼容数据库上使用 pgvector 的向量类型（`vector` / `halfvec` / `sparsevec`）。

API 与 pgvector 完全一致，只是包名改为 `psycoudbtv`，并且为数据库驱动提供了两条并行的注册路径：

- `psycoudbtv.psycopg2` —— 对接原版 `psycopg2` 驱动
- `psycoudbtv.psycounvdb` —— 对接改名后的 `psycounvdb` 驱动（psycopg2 的改名版）

两者函数名都叫 `register_vector`，效果相同，各自只依赖同名的驱动。

## 安装（解压到 site-packages）

本包是纯 Python，架构无关，支持 Python 3.8 ~ 3.13。直接把 `psycoudbtv/` 目录放到 `site-packages` 下即可：

```bash
SP=$(python3 -c 'import site; print(site.getsitepackages()[0])')
cp -r psycoudbtv "$SP/"
python3 -c "import psycoudbtv; print('psycoudbtv OK', psycoudbtv.__all__)"
```

也可以用打好的发布 zip 解压到同一位置。

## 快速使用

```python
import psycounvdb                                   # 或 import psycopg2
from psycoudbtv.psycounvdb import register_vector    # 或 from psycoudbtv.psycopg2 import register_vector
import numpy as np

conn = psycounvdb.connect(host="localhost", port=5678, dbname="unvdb", user="unvdb")
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

cur.execute("CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3))")
cur.execute("INSERT INTO items (embedding) VALUES (%s)", (np.array([1, 2, 3]),))
cur.execute("SELECT id, embedding FROM items ORDER BY embedding <-> %s LIMIT 5", (np.array([1, 2, 3]),))
print(cur.fetchall())
```

更详细的逐步连接测试见 `psycoudbtv-连接测试文档.md`。

## 与上游的差异

- 顶层包 `pgvector/` 重命名为 `psycoudbtv/`，`pyproject.toml` 中 `name` 改为 `psycoudbtv`。
- `requires-python` 下调到 `>= 3.8`，并为各驱动适配文件补充 `from __future__ import annotations`，使其在 Python 3.8/3.9 上也能导入。
- 新增 `psycoudbtv/psycounvdb/` 子模块，对接 `psycounvdb` 驱动；`psycoudbtv/psycopg2/` 仍对接原版 `psycopg2`。

## 许可

继承上游 pgvector-python 的 MIT 许可，见 `LICENSE.txt`。
