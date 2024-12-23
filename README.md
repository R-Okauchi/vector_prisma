# vector-prisma
prismaのpgvector拡張をパラメトリックに扱うためのラッパーモジュール

## 使用方法
pythonモジュールで利用できる

（例）

```bash
poetry add git+https://github.com/R-Okauchi/vector-prisma.git
```

### ファイルの生成

schema.prismaが存在するディレクトリにおいて

```jsx
vector-prisma generate
```

### clientのスタート

```python
from vector_prisma import VectorPrisma

prisma = VectorPrisma()
```

これで他のテーブルの操作も元々のprismaのメソッドで行える

### 各メソッドの使い方例

baseのmodelとCreateInput, UpdateInput, UpsertInputあたりはvector_prisma/typesからインポートする必要がある

```python
from prisma.types import UserEmbeddingWhereInput
from vector_prisma import VectorPrisma
from vector_prisma.models import UserEmbedding
from vector_prisma.types import (
    UserEmbeddingCreateInput,
    UserEmbeddingUpsertInput,
)

from models.user_embedding import UserEmbeddingCreate

async def create_user_embedding(
    prisma: VectorPrisma, embedding: UserEmbeddingCreate
) -> UserEmbedding:
    data = UserEmbeddingCreateInput(embedding.model_dump())
    return await prisma.userembedding_vec.create(data)

async def read_user_embeddings(
    prisma: VectorPrisma, filter: UserEmbeddingWhereInput = {}
) -> list[UserEmbedding]:
    return await prisma.userembedding_vec.find_many(where=filter)

async def bulk_upsert_User_embeddings(
    prisma: VectorPrisma, data_list: list[UserEmbeddingCreate] = []
) -> dict[str, int]:
    async with prisma.tx_vec() as transaction:
        results = []
        for data in data_list:
            result = await transaction.userembedding_vec.upsert(
                where={"user_id": str(data.user_id)},
                data=UserEmbeddingUpsertInput(data.model_dump()),
            )
            results.append(result)

    return {"count": len(results)}

```

### 現状対応しているメソッド

- create
- update
- upsert
- update
- find_many
- delete
- retrieve
    - ベクトル配列をresponseに含んだ近似最近傍探索
- retrieve_slim
    - ベクトル配列をresponseに含まない近似最近傍探索


## retrievalメソッド

以下のように、検索クエリのembeddingを渡すことで近似最近傍探索ができる。

探索用の距離関数には以下が用意されている。

- L1_DISTANCE（マンハッタン距離）
- L2_DISTANCE（ユークリッド距離）
- INNER_PRODUCT（ベクトル間内積）
- COSINE_DISTANCE（コサイン距離）

```python
from vector_prisma import VectorPrisma
from vector_prisma.operations import SearchMetric
from vector_prisma.vectors import UserEmbeddingVector

async def retrieve_nn_Users_slim(
    prisma: VectorPrisma,
    query_vec: UserEmbeddingVector.Vector,
    top_k: int,
    metric: SearchMetric,
) -> list[tuple[str, float]]:
    """user id と，distanceだけ返す"""
    records = await prisma.userembedding_vec.retrieve_slim(
        query_vec, "vec", top_k, metric
    )

    results = []

    for record in records:
        results.append((record.user_id, record.distance))
    
    return results
```