# psycoudbtv 连接测试文档

本文档说明如何把 `psycoudbtv`解压到 site-packages 并对 UNVDB 数据库做一次基本的向量连接测试。下述步骤已在 aarch64 / Python 3.13 + UNVDB 上实测通过。

---

## 1. 前提条件

- Python 3.8 ~ 3.13（任意一个即可，纯 Python 包，架构无关）
- 已安装数据库驱动（二选一，按你要测的路径准备）：
  - `psycopg2` / `psycopg2-binary`
  - 或你的 `psycounvdb`
- 已安装 `numpy`
- UNVDB 已启动，且已安装 `vector` 扩展

测试用连接信息（按实际环境替换）：

| 项 | 值 |
|---|---|
| host | `localhost` |
| port | `5678` |
| dbname | `unvdb` |
| user | `unvdb` |
| password | 空（trust 认证） |

---

## 2. 安装：解压到 site-packages

包是一个解压即用的 zip：`psycoudbtv-0.4.2-py3.8-3.13.zip`，里面是顶层目录 `psycoudbtv/`。

### Linux

```bash
# 找到 site-packages
SP=$(python3 -c 'import site; print(site.getsitepackages()[0])')

# 解压进去（解压后是 $SP/psycoudbtv/）
python3 -m zipfile -e psycoudbtv-0.4.2-py3.8-3.13.zip "$SP/"
# 或：unzip psycoudbtv-0.4.2-py3.8-3.13.zip -d "$SP/"

# 验证
python3 -c "import psycoudbtv; print('psycoudbtv OK', psycoudbtv.__all__)"
```


### Windows (PowerShell)

```powershell
$SP = python -c "import site; print(site.getsitepackages()[0])"
Expand-Archive psycoudbtv-0.4.2-py3.8-3.13.zip -DestinationPath $SP
python -c "import psycoudbtv; print('psycoudbtv OK', psycoudbtv.__all__)"
```

---

## 3. 基本连接测试（手动逐行输入）

下面是在 **Python 交互式命令行**里一步步手动输入的过程，不需要写脚本文件。每一步都能立刻看到结果，便于定位问题。

### 第 0 步：进入 Python 交互环境

```bash
python3
```

看到 `>>>` 提示符后，逐行输入下面的命令。

### 第 1 步：导入驱动和 register_vector

两条路径二选一。

- **psycopg2**：

```python
>>> import psycopg2 as driver
>>> from psycoudbtv.psycopg2 import register_vector
```

- **psycounvdb**：

```python
>>> import psycounvdb as driver
>>> from psycoudbtv.psycounvdb import register_vector
```

### 第 2 步：连接数据库

```python
>>> conn = driver.connect(host="localhost", port=5678, dbname="unvdb", user="unvdb")
>>> conn.autocommit = True
>>> cur = conn.cursor()
>>> cur.execute("SELECT version()")
>>> cur.fetchone()[0]
'PostgreSQL 24.11 on aarch64-unknown-linux-gnu, compiled by gcc (GCC) 10.3.0, 64-bit'
```

### 第 3 步：确保 vector 扩展存在并注册向量类型

```python
>>> cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
>>> register_vector(conn)
```

`register_vector(conn)` 没有报错即注册成功。

### 第 4 步：建表并写入向量

```python
>>> import numpy as np
>>> cur.execute("CREATE TABLE pgv_demo (id bigserial PRIMARY KEY, embedding vector(3))")
>>> cur.execute("INSERT INTO pgv_demo (embedding) VALUES (%s)", (np.array([1, 2, 3]),))
>>> cur.execute("INSERT INTO pgv_demo (embedding) VALUES (%s)", (np.array([4, 5, 6]),))
>>> cur.execute("INSERT INTO pgv_demo (embedding) VALUES (%s)", (np.array([0.1, 0.2, 0.3]),))
```

### 第 5 步：最近邻查询（欧氏距离 `<->`）

```python
>>> cur.execute("SELECT id, embedding, embedding <-> %s AS dist FROM pgv_demo ORDER BY dist LIMIT 3", (np.array([1, 2, 3]),))
>>> for row in cur.fetchall():
...     print(row[0], row[1].to_list(), round(row[2], 4))
...
1 [1.0, 2.0, 3.0] 0.0
3 [0.10000000149011612, 0.20000000298023224, 0.30000001192092896] 3.3675
2 [4.0, 5.0, 6.0] 5.1962
```

返回的 `row[1]` 是 `Vector` 对象、距离正确，说明向量写入和读取都正常。

### 第 6 步：清理并退出

```python
>>> cur.execute("DROP TABLE pgv_demo")
>>> cur.execute("PURGE RECYCLEBIN") 
>>> cur.close()
>>> conn.close()
>>> exit()
```

---


## 4. 常见问题

- **`ModuleNotFoundError: No module named 'psycoudbtv'`**
  解压位置不对，确认 `psycoudbtv/` 目录就在 site-packages 下：`python3 -c "import site; print(site.getsitepackages())"`。

- **`ModuleNotFoundError: No module named 'psycounvdb'`（或 'psycopg2'）**
  对应的数据库驱动没装。装上你要用的那个驱动，或改用另一条 import 路径。

- **`relation "..._pkey" already exists in schema "recyclebin"`**
  UNVDB 的回收站机制残留。执行 `PURGE RECYCLEBIN;`，或建表用不重名的表名。

- **连接超时 / 拒绝**
  检查端口（UNVDB 默认 5678）、`unvdbsvr` 是否在跑、`pg_hba`/防火墙是否放行。
