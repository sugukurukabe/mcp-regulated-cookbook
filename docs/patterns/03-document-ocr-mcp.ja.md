---
title: "文書OCRおよび構造化データ抽出用MCPツール"
status: draft
version: 0.1.0
last_reviewed: 2026-04-27
spec_version: "2025-11-25"
domains:
  - immigration
  - finance
  - labor
  - healthcare
platforms_tested:
  - "Google Cloud Document AI"
  - "Google Cloud Run"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
---

# パターン 03: 文書OCRおよび構造化データ抽出用MCPツール

> **一文要約.** 認識不可能な文書タイプに対してはLLMのフォールバックを組み込みつつ、Cloud Document AIの機能をMCPツールとして公開し、ファイルの取り込みと構造化スキーマの抽出を処理します。

## いつこのパターンを使うべきか

以下の条件に当てはまる場合、このパターンの対象となります。

- 物理的な文書（在留カード、パスポート、領収書、請求書）を取り込み、構造化データを抽出するMCPサーバーが必要である。
- データの抽出精度がその後の手続きの適法性を左右する規制領域で事業を展開している（例：ビザの有効期限の抽出など）。
- エージェントループを破壊することなく、テキストベースのMCP通信とバイナリファイルのアップロードのギャップを埋めたい。

## 課題（Forces）

- **決定論的OCR vs 確率論的LLM:** 専用に構築されたOCRプロセッサ（Document AIのInvoiceパーサーやIDパーサーなど）は、生の画像をマルチモーダルLLMに渡すよりも、構造化抽出において決定論的であり監査適性が高いです。
- **レイテンシ vs ユーザー体験:** 高精度のOCR API呼び出しには10〜30秒かかる場合があります。エージェントループ内では、MCPクライアントのトランスポートをタイムアウトさせることなく、このレイテンシを処理する必要があります。
- **テキストプロトコルでのファイル処理:** MCPはテキストベースのプロトコルです。バイナリの画像やPDFは、Base64エンコードされたペイロード、または署名付きURL経由で取り込む必要があります。

## 解決策

**推奨事項.** 外部参照（Google Cloud StorageのURIやBase64データなど）を受け取るツールの背後に文書抽出機能をラップします。文書のタイプに基づいて、専用のCloud Document AIプロセッサに文書を送信します。文書タイプが専用プロセッサでサポートされていない場合は、厳密な出力スキーマを持つマルチモーダルLLM（Geminiなど）に優雅にフォールバックさせます。

```python
# 説明用疑似コード
@mcp.tool(name="extract_document_data")
async def extract_document_data(gcs_uri: str, document_type: str) -> dict:
    # 1. 専用プロセッサへのルーティング
    if document_type == "invoice":
        processor_id = os.environ["DOCUMENT_AI_PROCESSOR_INVOICE_ID"]
        result = await call_document_ai(processor_id, gcs_uri)
    elif document_type == "id_card":
        processor_id = os.environ["DOCUMENT_AI_PROCESSOR_OCR_ID"]
        result = await call_document_ai(processor_id, gcs_uri)
    else:
        # 2. カスタム抽出のためにGeminiへフォールバック
        if os.environ.get("DOCUMENT_AI_USE_FALLBACK_GEMINI") == "true":
            result = await call_gemini_extraction(gcs_uri, document_type)
        else:
            raise ValueError("サポートされていない文書タイプです")
            
    # 3. 構造化スキーマを返す
    return {"status": "success", "extracted_data": result}
```

## トレードオフ

- **運用コスト:** Document AIの専用プロセッサのバージョンを保守および更新するには、継続的な監視が必要です。
- **パフォーマンスコスト:** 同期OCR処理はツールの実行をブロックします。処理が60秒を超えると、トランスポートのタイムアウトリスクが発生する可能性があります。

## このパターンが失敗するケース

- **失敗モード: 大きなファイルでのクライアントのタイムアウト。** OCR処理にMCPクライアントのタイムアウトウィンドウより長い時間がかかった場合、バックグラウンドでの処理は成功しても、エージェントはエラーを受け取ります。対策: 大規模なバッチジョブの場合は、ジョブIDを返す非同期パターンを使用します。

## 本番環境での採用実績

- [**Case Study 01: スグクル株式会社**](../case-studies/01-sugukuru.ja.md) — `sugukuru-core` サーバーは Document AI (`DOCUMENT_AI_ENABLED=true`) 経由でこのパターンを利用しています。IDカードや請求書を専用プロセッサ (`DOCUMENT_AI_PROCESSOR_OCR_ID`, `DOCUMENT_AI_PROCESSOR_INVOICE_ID`) にルーティングする一方で、エッジケース用に明示的にGeminiフォールバックフラグ (`DOCUMENT_AI_USE_FALLBACK_GEMINI=true`) を維持しています。
