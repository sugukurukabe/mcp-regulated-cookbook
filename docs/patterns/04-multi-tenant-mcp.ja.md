---
title: "MCPのマルチテナントアーキテクチャ: コンテキストにバインドされたデータ分離"
status: stable
version: 1.0.0
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
domains:
  - finance
  - hr
  - healthcare
  - public-sector
  - saas
platforms_tested:
  - "Supabase (PostgreSQL RLS)"
  - "FastMCP (Python ContextVar)"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
---

# パターン 04: MCPのマルチテナントアーキテクチャ: コンテキストにバインドされたデータ分離

> **一文要約.** LLMの入力に依存せず、トランスポート層でのテナント識別情報を非同期コンテキスト変数にバインドし、DBクエリとRLS（行レベルセキュリティ）層で自動強制することで、MCPサーバー内のテナントデータを安全に分離します。

## いつこのパターンを使うべきか

以下の条件に当てはまる場合、このパターンの対象となります。
- B2B SaaSや、複数のクライアント組織（テナント）にサービスを提供するMCPサーバーを構築している。
- 「テナントAを代理するAIエージェントが、テナントBのデータをクエリしたり、更新・削除したりできないこと」を物理的に保証する必要がある。
- 呼び出し元クライアントの識別に、接続レベルの認証（APIキー、OAuthトークンなど）を使用している。

以下の場合は**対象外**です。
- 単一の組織（シングルテナント）専用のMCPサーバー、またはローカルの個人データのみを扱う場合。
- ツールがアクセス制限のないオープンな公開データのみを操作する場合。

## 課題（Forces）

- **LLMのハルシネーション vs セキュリティ:** もし `get_staff_list(org_id: str)` のようなツールを設計した場合、`org_id` を渡す責任はLLMに委ねられます。ハルシネーションやプロンプトインジェクションによってLLMが他社のIDを渡してしまった場合、致命的なデータ漏洩（情報漏えい）につながります。
- **プロトコルの制限:** 現在のMCPの仕様には、「テナントコンテキスト」に関するネイティブな標準定義が存在しません。
- **開発者の人間的エラー:** 何十ものMCPツールにおいて、開発者が手動ですべてのSQLクエリに `where org_id = current_tenant` を追加することを期待すると、必ずフィルタの付け忘れによるセキュリティインシデントが発生します。

## 解決策

**推奨事項.** 決してLLMにセキュリティの境界を定義させないでください。トランスポートの接続フェーズ（APIキーなど）でテナントの識別情報を抽出し、それを非同期コンテキスト変数に保存します。そして、ラップされたデータベースクライアントと PostgreSQL の Row Level Security (RLS) を通じて、すべてのデータベース操作にその識別情報を「自動的に注入」します。

### 確実な実装の証拠（The Implementation Proof）

これは机上の空論ではありません。スグクル株式会社では、このパターンを用いて「JAきもつき」や「WIN国際協同組合」といった複数企業の厳格に規制された人事・ビザデータを処理しています。以下はその実際のコードベースからの証拠です。

#### 1. トランスポート＆コンテキスト層 (Python `ContextVar`)
MCP接続が確立されるとAPIキーが検証され、`org_id` がスレッドセーフ/非同期セーフな `ContextVar` に保存されます。LLMがこのIDを見ることは一切ありません。

```python
# 証拠元: /src/sugukuru_hub/tenant.py
from contextvars import ContextVar

_current_tenant: ContextVar[Optional["TenantContext"]] = ContextVar("_current_tenant", default=None)

async def resolve_tenant_by_api_key(api_key: str) -> Optional[TenantContext]:
    # 例: 'sk-ja-kimotsuki-001' を '00000000-...-0002' に解決
    result = supabase.table("organizations").select("*").eq("api_key", api_key).single().execute()
    # ...
```

#### 2. アプリケーション層での自動注入
データベースクライアントはすべての標準的な操作（SELECT、INSERT、UPDATE）をラップし、テナントフィルタを自動的に注入します。ツールを作成する開発者はただ `db.select("staff")` と呼ぶだけで、内部的に安全に `select * from staff where org_id = '...'` に変換されます。

```python
# 証拠元: /src/sugukuru_hub/tools/supabase_client.py
def _inject_org_id_filter(self, table: str, params: dict) -> dict:
    """テナントテーブルに org_id フィルタを自動注入"""
    if table in TENANT_TABLES and "org_id" not in params:
        org_id = get_org_id() # ContextVar から読み取る
        if org_id:
            params["org_id"] = f"eq.{org_id}"
    return params
```

#### 3. データベース層での強制実行 (PostgreSQL RLS)
多層防御（Defense-in-depth）として、クライアントトークンが使用された場合や、開発者がラッパーをバイパスしてしまった場合に備え、PostgreSQLのRow Level Security（RLS）がデータ分離をデータベースレベルで絶対的に保証します。

```sql
-- 証拠元: /supabase/migrations/016_multi_tenant.sql
CREATE OR REPLACE FUNCTION get_current_org_id() RETURNS UUID AS $$
BEGIN
    RETURN (auth.jwt() -> 'app_metadata' ->> 'org_id')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

CREATE POLICY "staff_tenant" ON staff FOR ALL TO authenticated
    USING (org_id = get_current_org_id())
    WITH CHECK (org_id = get_current_org_id());
```

## トレードオフ

- **実装のオーバーヘッド:** データベースクライアントや ORM をラップする層を構築する必要があります。
- **ツールテストの複雑化:** トランスポート層の API キーや `ContextVar` への注入をモック（模倣）しない限り、MCP ツールを単体でテストすることが難しくなります。

## このパターンが失敗するケース

- **失敗モード: グローバルなダッシュボードクエリ。** 内部管理者が「すべてのテナントを横断して」総アクティブユーザー数などをクエリするMCPツールが必要になった場合、このパターンの厳格な分離がクエリをブロックします。明示的に内部向けの「特権管理者バイパス」を作成する必要がありますが、これには高いリスクが伴います。

## 本番環境での採用実績

- [**Case Study 01: スグクル株式会社**](../case-studies/01-sugukuru.ja.md) — `sugukuru`, `ja-kimotsuki`, `win-international` などの組織をまたいで稼働する100以上のMCPツール（`aios` Pythonコードベースにて115のユニークなツール定義を検証済み）。コードベースは、この `ContextVar` + 自動 `org_id` 注入 + RLS の組み合わせを通じて、62のテナント分離テーブルにわたり、外国人労働者の個人情報（PII）、ビザのステータス、財務記録を完全に分離・保護しています。

## 変更履歴

- **1.0.0** (2026-04-28) — 初版公開。`sugukuru_hub` のマルチテナントアーキテクチャから抽出。
