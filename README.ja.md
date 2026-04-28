# mcp-regulated-cookbook

> 移民・入管、金融、労働・労務などの規制領域における、Model Context Protocol (MCP) サーバーの本番運用向け再利用可能パターン集。

このクックブックは、AIの機能性と同様に安全性、コンプライアンス、監査性が重要視される環境において、MCPサーバーを展開するためのアーキテクチャパターンとケーススタディを集めたものです。

**基本原則**: このクックブックに記載されるすべてのパターンは、少なくとも1つの本番環境デプロイによって裏付けられていなければなりません。純粋な理論上のアーキテクチャは公開しません。

## 収録内容

### パターン (Patterns)
- [Pattern 01: Cloud Run におけるマルチインスタンスのセッション継続性](docs/patterns/01-cloud-run-multi-instance.ja.md)
- [Pattern 02: 規制業務向けツール・アノテーション](docs/patterns/02-tool-annotations-regulated.ja.md)
- [Pattern 03: 文書OCRおよび構造化データ抽出用MCPツール](docs/patterns/03-document-ocr-mcp.ja.md)
- [Pattern 04: MCPのマルチテナントアーキテクチャ: コンテキストにバインドされたデータ分離](docs/patterns/04-multi-tenant-mcp.ja.md)

### ケーススタディ (Case Studies)
- [Case Study 01: スグクル株式会社](docs/case-studies/01-sugukuru.ja.md)

## 貢献について (Contributing)

パターンやケーススタディの提案方法については [CONTRIBUTING.md](CONTRIBUTING.md)（英語）をご参照ください。私たちは「本番環境での裏付け（Production Grounding）」という厳格なルールを遵守しています。実際のデプロイでテストされていないものは、安定版パターンとして採用されることはありません。

## ライセンス

Apache 2.0
