---
title: "スグクル株式会社: 日本の特定技能ビザおよび人材派遣業務向けの3つのPython MCPサーバーとWhatsApp Webhook"
attribution: attributed
status: published
last_reviewed: 2026-04-27
patterns_validated:
  - 01-cloud-run-multi-instance
  - 04-multi-tenant-mcp
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO)"
license: "Apache-2.0; case study text additionally attributable to Sugukuru Inc."
---

# ケーススタディ 01: スグクル株式会社

> Cloud Run `asia-northeast1` 上で稼働する、3つの Python FastMCP サーバー、REST API ハブ、および WhatsApp Webhook レシーバー。2026年3月より本番運用中であり、日本の出入国管理法に基づくビザ、財務、および CRM 操作を400名以上の外国人労働者向けにサポートしています。

## 概要

| 項目 | 内容 |
|---|---|
| 組織 | スグクル株式会社 (Sugukuru Inc.)、鹿児島県 |
| 産業 | 農業従事者の人材派遣（特定技能） |
| 本番稼働中のMCPサーバー | 3つ (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`) |
| サポートサービス | 2つ (`sugukuru-hub` REST API, `sugukuru-comms` Webhook) |
| プラットフォーム | Google Cloud Run, リージョン `asia-northeast1` |
| ランタイム | Python 3.12 (MCPサーバー) / Node.js (comms) |
| MCPトランスポート | `streamable_http` (ステートフル) |
| セッション継続戦略 | Pattern 01 — ハイブリッド: `core` に Path A (ウォームベースライン, Min: 1)、`finance`/`crm` に Path B (ゼロスケール, Min: 0)。Cloud Run ネイティブのスティッキーセッション。外部セッションストア不使用。 |
| 本番開始日 | `core`/`finance`/`crm`: 2026-03-22 |

## 運用内容とその理由

スグクルは規制の厳しい業界で活動する小規模事業者です。MCP主導の業務オペレーションの対象となるアクティブな外国人労働者（ビザ申請、派遣契約、給与台帳の管理対象）は**400名以上**です（Supabase `staff` テーブルにて確認、 2026年4月）。

MCP のフリートは、3つの Python `FastMCP` サーバーに分割されており、REST API ハブと Node.js の WhatsApp Webhook によってサポートされています。

- **`sugukuru-core`** (MCP) — 人事記録、ビザ申請ケース、書類生成。
- **`sugukuru-finance`** (MCP) — freee および GMO あおぞらネット銀行との統合。認証境界や監査要件が異なるため分離されています。
- **`sugukuru-crm`** (MCP) — セールスパイプライン、クライアント記録、派遣先管理。
- **`sugukuru-hub`** (REST API) — 外部ツールとの内部統合を保持する統合用 API ハブ。
- **`sugukuru-comms`** (Webhook) — WhatsApp Business API の Webhook レシーバーとして機能する、標準的な Express アプリ。以前のドキュメントの下書きとは異なり、これは MCP サーバーではなく、MCP ツールを一切含んでいません。厳格に受信メッセージのルーティングのみを行っています。

## 2026年4月現在の Cloud Run 構成

すべての Python MCP サービスは Cloud Run `asia-northeast1` 上で、`containerConcurrency: 80` の設定で稼働しています。

スケーリング構成:

| サービス | 最小インスタンス | 最大インスタンス | セッションアフィニティ | ランタイム |
|---|---|---|---|---|
| `sugukuru-core` (MCP) | **1** | 20 | true | Python 3.12 |
| `sugukuru-finance` (MCP) | 0 | 20 | true | Python 3.12 |
| `sugukuru-crm` (MCP) | 0 | 20 | true | Python 3.12 |
| `sugukuru-comms` (Webhook) | — | — | 不明 | Node.js |

> **証拠元:** GCPコンソール Cloud Run Observability タブのスクリーンショット、2026-04-28 キャプチャ。初回デプロイスクリプト (`deploy-mcp-split.sh`) では `--min-instances=0 --max-instances=10` と指定されていますが、実際の本番環境ではデプロイ後に上記のとおりチューニングされています。

すべての MCP サーバーは `--session-affinity` を使用しています。`core` はユーザー向けの主要エントリポイントとして Path A (`min-instances: 1`) を使用しコールドスタートレイテンシを排除、`finance` と `crm` はアイドルコストゼロの Path B (`min-instances: 0`) を使用しています。これは [Pattern 01](../patterns/01-cloud-run-multi-instance.ja.md) の本番実現例です。SDK のインメモリのセッションマップが唯一の Single Source of Truth（信頼できる唯一の情報源）として維持されています。このデプロイメントには、**Memorystore Redis や Firestore など、外部セッションストアは一切存在しません**。

> **注記:** `sugukuru-comms` はメインのデプロイスクリプト (`deploy-mcp-split.sh`) とは別に管理されており、そのCloud Run構成はここでは独立に検証されていません。

## 驚いた点・発見

**プロジェクトの memo は嘘をつくが、YAML は嘘をつかない。** このプロジェクトの引き継ぎ用メモには、いくつかの不正確な技術的主張が含まれていました。Bun 上で TypeScript を使用していると主張していましたが、実際には Python 3.12 と FastMCP を使用していました。また、`core` に対して `min-instances: 1` が設定されていると主張していましたが、実際には `0` でした。さらに `comms` が `openWorldHint` ツールを持つ MCP サーバーであると主張していましたが、実際にはツールを持たない標準的な Express Webhook でした。この Cookbook が実際に検証された事実を提供することを保証するために、メモとコードベースおよび Cloud Run デプロイスクリプトを照合・修正する規律が極めて重要でした。

## このケーススタディが検証するパターン

- [Pattern 01: Cloud Run Multi-Instance Session Continuity](../patterns/01-cloud-run-multi-instance.ja.md), v0.3.0 — ハイブリッド: `core` に Path A（ウォームベースライン）、`finance`/`crm` に Path B（ゼロスケール）。このケーススタディは、GCPコンソールのスクリーンショットによる両パスの本番証拠を提供します。コンテナ起動レイテンシメトリクスも含みます（p50: ~5秒、p99: `core` で最大30秒）。
- [Pattern 04: MCPのマルチテナントアーキテクチャ](../patterns/04-multi-tenant-mcp.ja.md), v1.0.0 — `aios` コードベースは、ContextVar + 62のテナント分離テーブルへの自動 `org_id` 注入 + PostgreSQL RLS による多層防御を実装しています。パイロットテナント（JAきもつき、WIN国際協同組合）が本番環境に設定・シード済みです。

## データベースインフラストラクチャ

すべての MCP サーバーは、`ap-southeast-1`（シンガポール）にホスティングされた単一の **Supabase** インスタンス（`sugukuru_ai_os`、MICRO プラン）に接続しています。

| メトリクス (7日間, 2026年4月) | 値 |
|---|---|
| 総リクエスト数 | **74,789** |
| データベースリクエスト | **65,666** (日平均 ~9,380) |
| 認証リクエスト | **8,700** (日平均 ~1,243) |
| アクティブDB接続数 | 9 / 60 |
| リソース利用率 | CPU 1%, Disk 11%, RAM 50% |
| 最新マイグレーション | `production_master_cleanup_20260425` |
| プラン | Supabase Micro (`t4g.micro`) |

> **証拠元:** Supabase ダッシュボードのスクリーンショット、2026-04-28 キャプチャ。

特筆すべき点: MCPフリート全体 — 117のツール、400名以上の労働者記録、マルチテナントRLS分離 — が、**月額$25の Supabase Micro インスタンス**上でCPU 1%、RAM 50%で稼働しています。これは、本番グレードの規制対応MCPオペレーションに高価なインフラが不要であることの強力な証拠です。

## 月額インフラコスト合計

| コンポーネント | 月額コスト (2026年4月) |
|---|---|
| **Cloud Run** (3 MCPサーバー + hub + comms) | ¥25,400 (~$162 USD) |
| **Supabase** (Micro プラン) | ~$25 USD |
| **外部セッションストア (Redis等)** | $0 (不使用) |
| **合計見積もり** | **~$187 USD/月** |

> **証拠元:** GCP Billing Reports (2026年4月1日〜26日)。Cloud Run コストには `sugukuru-core` (Min: 1 ウォームインスタンス)、`sugukuru-finance`、`sugukuru-crm` (両方 Min: 0)、`sugukuru-hub`、`sugukuru-comms` が含まれます。

400名以上の外国人労働者のPII、ビザのステータス、財務記録を117のMCPツールとマルチテナント分離で管理するプラットフォームとして、インフラ総コストが月額$200未満であることは、エンタープライズグレードのMCPデプロイメントが経済的にアクセス可能であることを実証しています。

## CI/CDパイプライン

コンパニオンの TypeScript MCPプロジェクト (`suguvisa-mcp`) は、すべてのプッシュで GitHub Actions CI パイプラインを実行します:

- **CI Run #58**: `build-and-test` ジョブ — 成功、合計2分14秒
- ステップ: checkout → pnpm setup → Node.js setup (12秒) → 依存関係インストール (4秒) → Build (1分8秒) → Test (36秒)
- トリガー: `on: push` (全コミットに対して必須)

> **証拠元:** GitHub Actions ログ、`suguvisa-mcp` リポジトリ、2026-04-28 キャプチャ。

これは [Pattern 02](../patterns/02-tool-annotation-ci-audit.ja.md) の「CIによるツールアノテーション遵守の強制」アプローチを検証するものです。

## 変更履歴

- **2026-04-27** — 初版公開。初期の社内メモにあった多数のアーキテクチャ上の不正確な記述を照合し修正。全体にわたってゼロスケール構成を持つ Python FastMCP スタックであることを確認。
