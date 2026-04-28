---
title: "Cloud Run におけるマルチインスタンスのセッション継続性"
status: stable
version: 0.3.0
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
domains:
  - immigration
  - labor
  - agriculture
  - other
platforms_tested:
  - "Google Cloud Run (asia-northeast1)"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
evidence:
  - "GCPコンソール スクリーンショット (2026-04-28) — sugukuru-core, sugukuru-finance, sugukuru-crm"
  - "deploy-mcp-split.sh (初回デプロイスクリプト)"
---

# パターン 01: Cloud Run におけるマルチインスタンスのセッション継続性

> **一文要約.** Cloud Run ネイティブの `sessionAffinity: true` を使用し、最重要サービスにはウォームベースライン (`min-instances: 1`)、コスト重視のサービスにはゼロスケール (`min-instances: 0`) を組み合わせることで、`mcp-session-id` を失わずにステートフルな MCP `streamable_http` サーバーを稼働させます。

## いつこのパターンを使うべきか

以下の条件に当てはまる場合、このパターンの対象となります。

- 水平スケーリング可能なサーバーレスプラットフォーム（Google Cloud Run）に MCP サーバーをデプロイしている。
- ステートフルなセッションを持つ `streamable_http` トランスポートを使用している。
- 負荷に応じて複数インスタンスが立ち上がるオートスケール設定を行っている。
- 水平スケーリング時のセッション信頼性とクラウドコストのバランスを取りたい。

以下の場合は**対象外**です。

- 単一の VM または常に稼働している単一コンテナで運用している。
- すでに完全なステートレスモードへ移行済みである。
- `stdio` トランスポートのみを使用している。

## 課題（Forces）

- **コスト vs セッションの継続性:** `min-instances: 0` は最もコストが低い設定ですが、コールドスタートのレイテンシが発生します（本番環境で5〜10秒を観測）。`min-instances: 1` はコールドスタートを排除しますが、サービスあたり月額約$15〜30のコストがかかります。
- **Cloud Run ネイティブのセッションアフィニティ:** Cloud Run は、`--session-affinity` により、セッションのトラフィックを同じインスタンスに固定するCookieベースのセッションアフィニティをサポートしています。
- **外部セッションストアのコスト vs レイテンシ:** Redis などのセッションストレージを追加すると、1〜5ミリ秒のレイテンシと新たな障害ポイントが増加します。
- **サービスの重要度の非対称性:** MCPサーバーフリート内のすべてのサービスが同じ可用性要件を持つわけではありません。

## 解決策

**推奨事項.** Cloud Run ネイティブのスティッキーセッション (`--session-affinity`) を使用し、**サービスごとのスケーリング戦略**を採用します。最も重要な MCP サーバー（ユーザーが最初に、最も頻繁に接続するサービス）には `min-instances: 1` を設定し、二次的なサービスには `min-instances: 0` を設定します。このハイブリッドアプローチは、スグクル株式会社の本番環境で検証済みであり、外部セッションストアなしでコストとコールドスタートのユーザー体験のバランスを取ります。

### Path A: 最重要サービスのウォームベースライン

ユーザーセッションの大部分を処理するプライマリ MCP サーバー向け:

```
本番環境で検証済み (GCPコンソール, 2026-04-28):
  sugukuru-core → Min: 1, Max: 20, session-affinity: true
```

セッションアフィニティのアノテーションは、Cloud Run サービスYAMLで確認済みです:

```yaml
# Cloud Run YAML タブ — sugukuru-core (行38-43)
annotations:
  autoscaling.knative.dev/maxScale: "10"
  run.googleapis.com/client-name: gcloud
  run.googleapis.com/client-version: 550.0.0
  run.googleapis.com/sessionAffinity: "true"        # ← 決定的証拠
  run.googleapis.com/startup-cpu-boost: "true"       # ← コールドスタート緩和
```

これにより、最初のユーザーリクエストでのコールドスタートレイテンシが排除されます。セッションアフィニティCookieが後続のリクエストをウォームインスタンスに固定します。負荷が高まると、Cloud Run が追加のインスタンスをスケールアップし、Cookieによって各セッションが割り当てられたインスタンスに固定され続けます。

**Path A を選ぶべき場合:**
- ユーザーが最初にアクセスするプライマリのエントリポイントである。
- 最初のリクエストでの5〜10秒のコールドスタートがUX上許容できない。
- 常時稼働インスタンス1台のコスト（月額約$15〜30）が許容範囲である。

### Path B: 二次サービスのゼロスケール

呼び出し頻度が低い、または時折のコールドスタートレイテンシが許容できる MCP サーバー向け:

```
本番環境で検証済み (GCPコンソール, 2026-04-28):
  sugukuru-finance → Min: 0, Max: 20, session-affinity: true
  sugukuru-crm     → Min: 0, Max: 20, session-affinity: true
```

これらのサービスはアイドル時にゼロにスケールダウンします。最初のリクエストでコールドスタートが発生します（本番メトリクスで観測された値: p50: ~5秒、p99: 最大10秒）。セッションアフィニティCookieが、新しく作成されたインスタンスにセッションを固定します。

**Path B を選ぶべき場合:**
- エージェントのワークフロー内で二次的に呼び出されるサービスである。
- 5〜10秒のコールドスタートレイテンシが許容できる。
- アイドルコストをゼロにしたい。

### 初回デプロイスクリプト vs 本番環境の現実

初回デプロイスクリプト (`deploy-mcp-split.sh`) はすべてのサービスに `--min-instances=0 --max-instances=10` を設定しています:

```bash
# deploy-mcp-split.sh L78-92（初回デプロイ時の設定）
gcloud run deploy "${SERVICE_NAME}" \
    --session-affinity \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --concurrency=80
```

しかし、2026-04-28 時点の GCP コンソールのスクリーンショットでは、本番設定が乖離していることが判明:
- `sugukuru-core` はデプロイ後に **Min: 1, Max: 20** に手動調整された。
- `sugukuru-finance` と `sugukuru-crm` は **Min: 0, Max: 20** のまま（Max のみ 10→20 に増加）。

この乖離そのものが、ドキュメント化すべきパターンです: **初回デプロイ後の運用チューニングは正常かつ想定内です。** デプロイスクリプトはベースラインとして機能しますが、本番設定はトラフィックパターンの観察とコールドスタートの痛みに基づいて進化します。

### Path C: セッションステートの外部化

Path A/B のキャパシティを超えて成長した場合や、`gcloud run deploy` によるリビジョン更新時のセッション消失を一切許容できない場合は、Memorystore for Redis のような共有セッションストアの導入が考えられます。ただし、Path A/B が失敗しているという明確な証拠がない限り、Path C への過剰なエンジニアリングは避けてください。

## 本番メトリクス (GCPコンソール, 2026-04-28)

| メトリクス | sugukuru-core | sugukuru-finance | sugukuru-crm |
|---|---|---|---|
| min-instances | 1 | 0 | 0 |
| max-instances | 20 | 20 | 20 |
| コンテナ起動 (p50) | ~5秒 | ~5秒 | ~5秒 |
| コンテナ起動 (p99) | ~30秒 | ~10秒 | ~10秒 |
| 最大観測インスタンス数 | ~20 | ~4 | ~4 |
| 外部セッションストア | なし | なし | なし |

> **証拠元:** GCPコンソール Cloud Run Observability タブ、過去30日間ビュー、2026-04-28 キャプチャ。スクリーンショットは `reference/screenshots/` に保管。

## トレードオフ

- **運用コスト:** Path A は常時稼働インスタンス1台分のコスト。Path B はアイドルコストゼロ。3つのMCPサーバー合計の Cloud Run コスト: **月額約¥25,400（約$162 USD）**（GCP Billing レポート、2026年4月、26日分の実績）。
- **パフォーマンスコスト:** Path B のコールドスタートは5〜10秒 (p50〜p99)。Path A は最初のインスタンスのコールドスタートを排除。Cloud Run の `startup-cpu-boost: "true"` アノテーション（YAMLで確認済み）により、起動時に追加CPUが割り当てられ、コールドスタート時間が短縮されます。
- **複雑性コスト:** リビジョンのロールアウト時に、古いインスタンスに固定されていた進行中のセッションが切断される。Path A/B 両方で発生。

## このパターンが失敗するケース

- **Path A/B の失敗: トラフィックがキャパシティの限界を超える場合。** 同時セッション数が `maxScale` の処理能力を超えると、固定不可能なインスタンスに割り当てられるセッションが発生。
- **Path A/B の失敗: リビジョン展開によるセッション無効化。** `gcloud run deploy` 中に、以前のリビジョンで進行中だったセッションが途中で強制終了される可能性。
- **Path B の失敗: ユーザー向けコールドスタート。** ゼロスケールサービスへの最初のリクエストがユーザー起点の場合、5〜10秒のコールドスタートがUXを低下させる。

## 本番環境での採用実績

- [**Case Study 01: スグクル株式会社**](../case-studies/01-sugukuru.ja.md) — Cloud Run `asia-northeast1` 上で Python/FastMCP を実行する3つの MCP サーバー。`core` は Path A (Min: 1)、`finance` と `crm` は Path B (Min: 0) を使用。すべてで `--session-affinity` を使用。外部セッションストアなし。GCPコンソールのスクリーンショットにより設定を確認済み。

## 変更履歴

- **0.3.0** (2026-04-28) — **GCPコンソール証拠に基づく重大修正。** `sugukuru-core` が実際には `min-instances: 1`（0ではない）で稼働していること、全サービスの `max-instances` が20（10ではない）であることを発見。デプロイスクリプトは初回設定のみであり、本番環境の設定は乖離していた。パターンを Path A（ウォーム）と Path B（ゼロスケール）の相補的ハイブリッドとして再構成。
- **0.2.1** (2026-04-27) — デプロイスクリプトのみに基づき、全サービスが `min-instances: 0` を使用していると誤記。v0.3.0 で修正。
- **0.2.0** (2026-04-27) — Path 別のアプローチに再構築。
